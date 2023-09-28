%%%% A 99 LINE TOPOLOGY OPTIMIZATION CODE BY OLE SIGMUND, JANUARY 2000 %%%
%%%% CODE MODIFIED FOR INCREASED SPEED, September 2002, BY OLE SIGMUND %%%
%%%% CODE MODIFIED FOR GUI COMPATIBILITY, September 2023, BY PAUL VIGNON %%%
function topGUI_SIMP(nelx,nely,volfrac,penal,rmin);

pyout = fileread("pyout.txt");vars = strsplit(pyout,"\n");
nelx = str2num(vars{1});nely = str2num(vars{2});volfrac = str2num(vars{3});penal = str2num(vars{4});rmin = str2num(vars{5});fixeddofstemp = str2num(vars{6});loads = str2num(vars{7});nbloads = str2num(vars{8});saveDir=vars{9};
curDir = pwd; strrep(curDir,'\','/'); t = strcat('/',datestr(now(),'yyyy-mm-dd HH_MM_SS'));
if strcmp(saveDir,curDir); fdname = strcat(curDir,t,' SIMP'); else; fdname = strcat(saveDir,t,' SIMP'); end;
mkdir(fdname);
pkg load io
% INITIALIZE
x(1:nely,1:nelx) = volfrac; loop = 0; change = 1.;
excelout(1,1)=cellstr('Objective');excelout(1,2)=cellstr('Volume Fraction');excelout(1,3)=cellstr('Change');
% START ITERATION
while change > 0.01      %% Stoping criteria

  loop = loop + 1;
  xold = x;
% FE-ANALYSIS
  [U]=FE(nelx,nely,x,penal,nbloads,loads,fixeddofstemp);
% OBJECTIVE FUNCTION AND SENSITIVITY ANALYSIS
  [KE] = lk;
  c = 0.;
  excelout(loop+1,1:3)=0.;
  for ely = 1:nely
    for elx = 1:nelx
      n1 = (nely+1)*(elx-1)+ely;
      n2 = (nely+1)* elx   +ely;
      dc(ely,elx)=0.;
      for nb = 1:nbloads
        Ue = U([2*n1-1;2*n1; 2*n2-1;2*n2; 2*n2+1;2*n2+2; 2*n1+1;2*n1+2],nb);
        c = c + x(ely,elx)^penal*Ue'*KE*Ue;
        dc(ely,elx) = dc(ely,elx)-penal*x(ely,elx)^(penal-1)*Ue'*KE*Ue;
      end
    end
  end
  excelout(loop+1,1)=c;
% FILTERING OF SENSITIVITIES
  [dc]   = check(nelx,nely,rmin,x,dc);
% DESIGN UPDATE BY THE OPTIMALITY CRITERIA METHOD
  [x]    = OC(nelx,nely,x,volfrac,dc);
% PRINT RESULTS
  change = max(max(abs(x-xold)));
  excelout(loop+1,2)=sum(sum(x))/(nelx*nely); excelout(loop+1,3)=change;
  output_txt=[' It.: ' sprintf('%4i',loop) ' Obj.: ' sprintf('%10.4f',c) ...
       ' Vol.: ' sprintf('%6.3f',sum(sum(x))/(nelx*nely)) ...
        ' ch.: ' sprintf('%6.3f',change ) '\n'];
  disp(output_txt)
  if loop == 1; output=fopen(strcat(fdname,'/_out.txt'),'w'); else; output=fopen(strcat(fdname,'/_out.txt'),'a'); end;
  fprintf(output,output_txt); fclose(output);
% PLOT DENSITIES
  colormap(gray); imagesc(-x); axis equal; axis tight; axis off; axes('visible','off','title',sprintf('Iteration %04i',loop));pause(1e-6);
% SAVE IMAGES
  flname = strcat(fdname,'/mono_Macro',num2str(loop,'%04i'),'.jpg');
saveas(gcf, flname, 'jpg');
end
cell2csv(strcat(fdname,t,'_SIMP_data.csv'),excelout);
%%%%%%%%%% OPTIMALITY CRITERIA UPDATE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [xnew]=OC(nelx,nely,x,volfrac,dc)
l1 = 0; l2 = 100000; move = 0.2;
while (l2-l1 > 1e-4)
  lmid = 0.5*(l2+l1);
  xnew = max(0.001,max(x-move,min(1.,min(x+move,x.*sqrt(-dc./lmid)))));
  if sum(sum(xnew)) - volfrac*nelx*nely > 0;
    l1 = lmid;
  else
    l2 = lmid;
  end
end
%%%%%%%%%% MESH-INDEPENDENCY FILTER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [dcn]=check(nelx,nely,rmin,x,dc)
dcn=zeros(nely,nelx);
for i = 1:nelx
  for j = 1:nely
    sum=0.0;
    for k = max(i-floor(rmin),1):min(i+floor(rmin),nelx)
      for l = max(j-floor(rmin),1):min(j+floor(rmin),nely)
        fac = rmin-sqrt((i-k)^2+(j-l)^2);
        sum = sum+max(0,fac);
        dcn(j,i) = dcn(j,i) + max(0,fac)*x(l,k)*dc(l,k);
      end
    end
    dcn(j,i) = dcn(j,i)/(x(j,i)*sum);
  end
end
%%%%%%%%%% FE-ANALYSIS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [U]=FE(nelx,nely,x,penal,nbloads,loads,fixeddofstemp)
[KE] = lk;
K = sparse(2*(nelx+1)*(nely+1), 2*(nelx+1)*(nely+1));
F = sparse(2*(nely+1)*(nelx+1),nbloads); U = zeros(2*(nely+1)*(nelx+1),nbloads);
for elx = 1:nelx
  for ely = 1:nely
    n1 = (nely+1)*(elx-1)+ely;
    n2 = (nely+1)* elx   +ely;
    edof = [2*n1-1; 2*n1; 2*n2-1; 2*n2; 2*n2+1; 2*n2+2; 2*n1+1; 2*n1+2];
    K(edof,edof) = K(edof,edof) + x(ely,elx)^penal*KE;
  end
end
% DEFINE LOADS AND SUPPORTS (HALF MBB-BEAM)
for nb = 1:nbloads
  F([loads(2*nb-1)],nb) = [loads(2*nb)];
end
fixeddofs   = fixeddofstemp;
alldofs     = [1:2*(nely+1)*(nelx+1)];
freedofs    = setdiff(alldofs,fixeddofs);
% SOLVING
U(freedofs,:) = K(freedofs,freedofs) \ F(freedofs,:);
U(fixeddofs,:)= 0;
%%%%%%%%%% ELEMENT STIFFNESS MATRIX %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [KE]=lk
E = 1.;
nu = 0.3;
k=[ 1/2-nu/6   1/8+nu/8 -1/4-nu/12 -1/8+3*nu/8 ...
   -1/4+nu/12 -1/8-nu/8  nu/6       1/8-3*nu/8];
KE = E/(1-nu^2)*[ k(1) k(2) k(3) k(4) k(5) k(6) k(7) k(8)
                  k(2) k(1) k(8) k(7) k(6) k(5) k(4) k(3)
                  k(3) k(8) k(1) k(6) k(7) k(4) k(5) k(2)
                  k(4) k(7) k(6) k(1) k(8) k(3) k(2) k(5)
                  k(5) k(6) k(7) k(8) k(1) k(2) k(3) k(4)
                  k(6) k(5) k(4) k(3) k(2) k(1) k(8) k(7)
                  k(7) k(4) k(5) k(2) k(3) k(8) k(1) k(6)
                  k(8) k(3) k(2) k(5) k(4) k(7) k(6) k(1)];
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This Matlab code was written by Ole Sigmund, Department of Solid         %
% Mechanics, Technical University of Denmark, DK-2800 Lyngby, Denmark.     %
% Please sent your comments to the author: sigmund@fam.dtu.dk              %
%                                                                          %
% The code is intended for educational purposes and theoretical details    %
% are discussed in the paper                                               %
% "A 99 line topology optimization code written in Matlab"                 %
% by Ole Sigmund (2001), Structural and Multidisciplinary Optimization,    %
% Vol 21, pp. 120--127.                                                    %
%                                                                          %
% The code as well as a postscript version of the paper can be             %
% downloaded from the web-site: http://www.topopt.dtu.dk                   %
%                                                                          %
% Disclaimer:                                                              %
% The author reserves all rights but does not guaranty that the code is    %
% free from errors. Furthermore, he shall not be liable in any event       %
% caused by the use of the program.                                        %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
