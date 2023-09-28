%%%%% A SOFT-KILL BESO CODE BY X. HUANG and Y.M. Xie  %%%%%
function topGUI_softbeso(nelx,nely,volfrac,er,rmin);
er=.2;
pyout = fileread("pyout.txt");vars = strsplit(pyout,"\n");
nelx = str2num(vars{1});nely = str2num(vars{2});volfrac = str2num(vars{3});penal = str2num(vars{4});rmin = str2num(vars{5});fixeddofstemp = str2num(vars{6});loads = str2num(vars{7});nbloads = str2num(vars{8});saveDir=vars{9};
curDir = pwd; strrep(curDir,'\','/'); t = strcat('/',datestr(now(),'yyyy-mm-dd HH_MM_SS'));
if strcmp(saveDir,curDir); fdname = strcat(curDir,t,' softbeso'); else; fdname = strcat(saveDir,t,' softbeso'); end;
mkdir(fdname);
pkg load io
% INITIALIZE
x(1:nely,1:nelx) = 1.; vol=1.; i = 0; change = 1.;
excelout(1,1)=cellstr('Objective');excelout(1,2)=cellstr('Volume Fraction');excelout(1,3)=cellstr('Change');
% START iTH ITERATION
while change > 0.001
  i = i + 1;  vol = max(vol*(1-er),volfrac);
  if i >1; olddc = dc; end
% FE-ANALYSIS
  [U]=FE(nelx,nely,x,penal,nbloads,loads,fixeddofstemp);
% OBJECTIVE FUNCTION AND SENSITIVITY ANALYSIS
  [KE] = lk;
  c(i) = 0.;
  excelout(i+1,1:3)=0.;
  for ely = 1:nely
    for elx = 1:nelx
      n1 = (nely+1)*(elx-1)+ely;
      n2 = (nely+1)* elx   +ely;
      dc(ely,elx)=0.;
      for nb = 1:nbloads
        Ue = U([2*n1-1;2*n1; 2*n2-1;2*n2; 2*n2+1;2*n2+2; 2*n1+1;2*n1+2],nb);
        c(i) = c(i) + 0.5*x(ely,elx)^penal*Ue'*KE*Ue;
        dc(ely,elx) = dc(ely,elx)+0.5*x(ely,elx)^(penal-1)*Ue'*KE*Ue;
      end
    end
 end
 excelout(i+1,1)=c(i);
% FILTERING OF SENSITIVITIES
[dc]   = check(nelx,nely,rmin,x,dc);
% STABLIZATION OF EVOLUTIONARY PROCESS
if i > 1; dc = (dc+olddc)/2.; end
% BESO DESIGN UPDATE
[x]    = ADDDEL(nelx,nely,vol,dc,x);
% PRINT RESULTS
if i>10;
 change=abs(sum(c(i-9:i-5))-sum(c(i-4:i)))/sum(c(i-4:i));
end
excelout(i+1,2)=sum(sum(x))/(nelx*nely); excelout(i+1,3)=change;
output_txt=[' It.: ' sprintf('%4i',i) ' Obj.: ' sprintf('%10.4f',c(i)) ...
       ' Vol.: ' sprintf('%6.3f',sum(sum(x))/(nelx*nely)) ...
        ' ch.: ' sprintf('%6.3f',change ) '\n'];
disp(output_txt)
if i == 1; output=fopen(strcat(fdname,'/_out.txt'),'w'); else; output=fopen(strcat(fdname,'/_out.txt'),'a'); end;
fprintf(output,output_txt); fclose(output);
% PLOT DENSITIES
  colormap(gray); imagesc(-x); axis equal; axis tight; axis off; axes('visible','off','title',sprintf('Iteration %04i',i)); pause(1e-6);
% SAVE IMAGES
  flname = strcat(fdname,'\mono_Macro',num2str(i,'%04i'),'.jpg');
saveas(gcf, flname, 'jpg');
end
cell2csv(strcat(fdname,t,'_softbeso_data.csv'),excelout);
%%%%%%%%%% OPTIMALITY CRITERIA UPDATE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [x]=ADDDEL(nelx,nely,volfrac,dc,x)
l1 = min(min(dc)); l2 = max(max(dc));
while ((l2-l1)/l2 > 1.0e-5)
   th = (l1+l2)/2.0;
   x = max(0.001,sign(dc-th));
   if sum(sum(x))-volfrac*(nelx*nely) > 0;
      l1 = th;
   else
      l2 = th;
   end
end
%%%%%%%%%% MESH-INDEPENDENCY FILTER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [dcf]=check(nelx,nely,rmin,x,dc)
dcf=zeros(nely,nelx);
for i = 1:nelx
  for j = 1:nely
    sum=0.0;
    for k = max(i-floor(rmin),1):min(i+floor(rmin),nelx)
      for l = max(j-floor(rmin),1):min(j+floor(rmin),nely)
       fac = rmin-sqrt((i-k)^2+(j-l)^2);
       sum = sum+max(0,fac);
       dcf(j,i) = dcf(j,i) + max(0,fac)*dc(l,k);
      end
    end
    dcf(j,i) = dcf(j,i)/sum;
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
% DEFINE LOADS AND SUPPORTS (Cantilever)
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
