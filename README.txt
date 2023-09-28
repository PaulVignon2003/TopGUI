Shortcuts :
- Select = LMB (Left Click)
- Select Line = Shift + LMB (with one element already selected)
- Move/Pan = Scroll Wheel Click
- Zoom = Scroll Wheel
- Deselect = RMB (Right Click)

Differences between the solvers :
- SIMP : Is the only solver that will show element densities other than 1 or 0. It gives great results but is slow, especially on larger meshes
- Soft-kill BESO (softbeso) : It is great for larger meshes, can give misleading designs for small meshes. Converges very fast, good for a first estimation
- Levelset : It is good at approximating the shape that other solvers would attain with a larger mesh (levelset 50x25 can give shapes similar to those given by softbeso 200x100, though less refined)

Known Issues :
- If, on the same node, you apply a constraint to one DOF and a load to the other DOF, only the latest one will be shown visually, but both still exist
- Output parameters (other than Volume Fraction) only apply to SIMP, as the ones used by softbeso and levelset have not been added to the GUI yet
- Pan/Zoom is laggy on large meshes, this is due to the way the mesh is display and a solution has not been found yet. This is the reason for the 22500 (equivalent to 150 x 150 elements) limitation
- If certain cases, the solver will not converge and may give nonsensical results. This is normal and is either caused by incorrect parameters for the study case (too high penalization can cause this) or the solver needing a bigger mesh to compute that case properly.


