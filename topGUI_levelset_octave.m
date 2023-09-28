%% TOPOLOGY OPTIMIZATION USING THE LEVEL-
%SET METHOD, VIVIEN J. CHALLIS 2009

 function [struc] = topGUI_levelset_octave(nelx,nely,volReq,stepLength,numReinit,topWeight)
pyout = fileread("pyout.txt");vars = strsplit(pyout,"\n");
nelx = str2num(vars{1});nely = str2num(vars{2});volReq = str2num(vars{3});penal = str2num(vars{4});rmin = str2num(vars{5});fixeddofstemp = str2num(vars{6});loads = str2num(vars{7});nbloads = str2num(vars{8});saveDir=vars{9};
stepLength=3,numReinit=2,topWeight=4;
pkg load image
pkg load io
 curDir = pwd; strrep(curDir,'\','/'); t = strcat('/',datestr(now(),'yyyy-mm-dd HH_MM_SS'));
 if strcmp(saveDir,curDir); fdname = strcat(curDir,t,' levelset'); else; fdname = strcat(saveDir,t,' levelset'); end;
 mkdir(fdname);
 % Initialization
 struc = ones(nely,nelx);
 [lsf] = reinit(struc);
 shapeSens = zeros(nely,nelx); topSens =zeros(nely,nelx);
 [KE,KTr,lambda,mu] = materialInfo();
 excelout(1,1)=cellstr('Objective');excelout(1,2)=cellstr('Volume Fraction');
 % Main loop:
 for iterNum = 1:200
 % FE-analysis, calculate sensitivities
 [U] = FE(struc,KE,nbloads,loads,fixeddofstemp);
 shapeSens(:)=0;topSens(:)=0;
 excelout(iterNum+1,1:2)=0.;
 for ely = 1:nely
  for elx = 1:nelx
  n1 = (nely+1)*(elx-1)+ely;
  n2 = (nely+1)* elx +ely;
    for i=1:nbloads
    Ue = U([2*n1-1;2*n1; 2*n2-1;2*n2; 2*n2+1;2*n2+2; 2*n1+1;2*n1+2],i);
    shapeSens(ely,elx) = shapeSens(ely,elx)- max(struc(ely,elx),0.0001)*Ue'*KE*Ue;
    topSens(ely,elx) = topSens(ely,elx) +struc(ely,elx)*pi/2*(lambda+2*mu)/mu/(lambda+mu)*(4*mu*Ue'*KE*Ue+(lambda-mu)*Ue'*KTr*Ue);
    end
  end
 end
 % Store data, print & plot information
 objective(iterNum) = -sum(shapeSens(:));
 volCurr = sum(struc(:))/(nelx*nely);
 excelout(iterNum+1,1)=objective(iterNum);excelout(iterNum+1,2)=volCurr;
 output_txt=[' It.: ' sprintf('%4i',iterNum) ' Compl.: ' sprintf('%10.4f',objective(iterNum)) ' Vol.: ' sprintf('%6.3f',volCurr) '\n'];
 disp(output_txt)
 if iterNum == 1; output=fopen(strcat(fdname,'/_out.txt'),'w'); else; output=fopen(strcat(fdname,'/_out.txt'),'a'); end;
 fprintf(output,output_txt); fclose(output);
 colormap(gray); imagesc(-struc,[-1,0]);axis equal; axis tight; axis off; axes('visible','off','title',sprintf('Iteration %04i',iterNum)); drawnow;
 flname = strcat(fdname,'\mono_Macro',num2str(iterNum,'%04i'),'.jpg');
 saveas(gcf, flname, 'jpg');

 % Check for convergence
 if iterNum > 5 && ( abs(volCurr-volReq)< 0.005 ) &&  all( abs(objective(end)-objective(end-5:end-1) ) < 0.01*abs(objective(end)) )
 cell2csv(strcat(fdname,t,'_levelset_data.csv'),excelout);
 return;
 end
 % Set augmented Lagrangian parameters
 if iterNum == 1
 la = -0.01; La = 1000; alpha = 0.9;
 else
     la = la - 1/La * (volCurr - volReq); La= alpha * La;
 end
 % Include volume sensitivities
 shapeSens = shapeSens - la + 1/La*(volCurr-volReq);
 topSens = topSens + pi*(la - 1/La*(volCurr-volReq));
 % Design update
 [struc,lsf] = updateStep(lsf,shapeSens,topSens,stepLength,topWeight);
 % Reinitialize level-set function
 if ~mod(iterNum,numReinit)
 [lsf] = reinit(struc);
 end
cell2csv(strcat(fdname,'/_data.csv'),excelout);
end
 %%---- REINITIALIZATION OF LEVEL-SETFUNCTION ----
 function [lsf] = reinit(struc)
 strucFull = zeros(size(struc)+2);strucFull(2:end-1,2:end-1) = struc;
 % Use "bwdist" (Image Processing Toolbox)
 lsf = (~strucFull).*(bwdist(strucFull)-0.5)-strucFull.*(bwdist(strucFull-1)-0.5);
 %%----- DESIGN UPDATE ----
 function [struc,lsf] = updateStep(lsf,shapeSens,topSens,stepLength,topWeight)
 % Smooth the sensitivities
 [shapeSens] = conv2(padarray(shapeSens,[1,1],'replicate'),1/6*[0 1 0; 1 2 1;0 1 0],'valid');
 [topSens] = conv2(padarray(topSens,[1,1],'replicate'),1/6*[0 1 0; 1 2 1; 0 1 0],'valid');
 % Load bearing pixels must remain solid -Bridge:
 % shapeSens(end,[1,round(end/2):round(end/2+1),end]) = 0;
 % topSens(end,[1,round(end/2):round(end/2+1),end]) = 0;
 % Design update via evolution
 [struc,lsf] = evolve(-shapeSens,topSens.*(lsf(2:end-1,2:end-1)<0),lsf,stepLength,topWeight);
 %%---- EVOLUTION OF LEVEL-SET FUNCTION----
 function [struc,lsf] = evolve(v,g,lsf,stepLength,w)
 % Extend sensitivites using a zero border
 vFull = zeros(size(v)+2); vFull(2:end-1,2:end-1) = v;
 gFull = zeros(size(g)+2); gFull(2:end-1,2:end-1) = g;
 % Choose time step for evolution based onCFL value
 dt = 0.1/max(abs(v(:)));
 % Evolve for total time stepLength * CFLvalue:
 for i = 1:(10*stepLength)
 % Calculate derivatives on the grid
 dpx = circshift(lsf,[0,-1])-lsf;
 dmx = lsf - circshift(lsf,[0,1]);
 dpy = circshift(lsf,[-1,0]) - lsf;
 dmy = lsf - circshift(lsf,[1,0]);
 % Update level set function using anupwind scheme
 lsf = lsf - dt * min(vFull,0).* ...
 sqrt( min(dmx,0).^2+max(dpx,0).^2+min(dmy,0).^2+max(dpy,0).^2 ) ...
 - dt * max(vFull,0) .*...
 sqrt( max(dmx,0).^2+min(dpx,0).^2+max(dmy,0).^2+min(dpy,0).^2 )...
 - w*dt*gFull;
 end
 % New structure obtained from lsf
 strucFull = (lsf<0); struc = strucFull(2:end-1,2:end-1);
 %%---- FINITE ELEMENT ANALYSIS ----
 function [U] = FE(struc,KE,nbloads,loads,fixeddofstemp)
 [nely,nelx] = size(struc);
 K = sparse(2*(nelx+1)*(nely+1), 2*(nelx+1)*(nely+1));
 F = sparse(2*(nely+1)*(nelx+1),nbloads); U =zeros(2*(nely+1)*(nelx+1),nbloads);
 for elx = 1:nelx
 for ely = 1:nely
 n1 = (nely+1)*(elx-1)+ely;
 n2 = (nely+1)* elx +ely;
 edof = [2*n1-1; 2*n1; 2*n2-1; 2*n2; 2*n2+1; 2*n2+2; 2*n1+1; 2*n1+2];
 K(edof,edof) = K(edof,edof) + max(struc(ely,elx),0.0001)*KE;
 end
 end
 % Define loads and supports - Bridge:
 for nb = 1:nbloads
  F([loads(2*nb-1)],nb) = [loads(2*nb)];
 end
fixeddofs = fixeddofstemp;
 % Solving
 alldofs = 1:2*(nely+1)*(nelx+1);
 freedofs = setdiff(alldofs,fixeddofs);
 U(freedofs,:) = K(freedofs,freedofs) \ F(freedofs,:);
 %%---- MATERIAL INFORMATION ----
 function [KE,KTr,lambda,mu] =materialInfo()
% Set material parameters, find Lamevalues
 E = 1.; nu = 0.3;
 lambda = E*nu/((1+nu)*(1-nu)); mu = E/(2*(1+nu));
% Find stiffness matrix "KE"
 k =[ 1/2-nu/6 1/8+nu/8 -1/4-nu/12 -1/8+3*nu/8 -1/4+nu/12 -1/8-nu/8 nu/6 1/8-3*nu/8];
 KE = E/(1-nu^2)*stiffnessMatrix(k);
 % Find "trace" matrix "KTr"
 k=[1/3 1/4 -1/3 1/4 -1/6 -1/4 1/6 -1/4];
 KTr = E/(1-nu)*stiffnessMatrix(k);
 %%---- ELEMENT STIFFNESS MATRIX ----
 function [K] = stiffnessMatrix(k)
 % Forms stiffness matrix from first row
 K=[k(1) k(2) k(3) k(4) k(5) k(6) k(7) k(8)
    k(2) k(1) k(8) k(7) k(6) k(5) k(4) k(3)
    k(3) k(8) k(1) k(6) k(7) k(4) k(5) k(2)
    k(4) k(7) k(6) k(1) k(8) k(3) k(2) k(5)
    k(5) k(6) k(7) k(8) k(1) k(2) k(3) k(4)
    k(6) k(5) k(4) k(3) k(2) k(1) k(8) k(7)
    k(7) k(4) k(5) k(2) k(3) k(8) k(1) k(6)
    k(8) k(3) k(2) k(5) k(4) k(7) k(6) k(1)];


