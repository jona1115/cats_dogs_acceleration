WSL uses a VHDX for storing the file system. As [this guy](https://stackoverflow.com/a/70948675/7265313) put it:
- It is allocated to a maximum size
- It is initialized with just a few kilobytes of structural data
- It grows dynamically as data is added, up to their maximum allocated size
- But, the kicker -- They do not automatically shrink when data is removed.

This means that when you add more stuff to WSL, it will slowly grow and grow in size and might not strink even when you remove the files in WSL. This can be a pain because then Windows will think it is running out of space.

So to fix this, we can strink the volume. Here is a summary of these posts on line [\[1\]](https://stackoverflow.com/questions/70946140/docker-desktop-wsl-ext4-vhdx-too-large) [\[2\]](https://superuser.com/questions/495294/compact-a-vhd-file-created-by-disk-management):
1. Close all WSL terminals, VScode with WSL, etc.
2. Open up Powershell, and shutdown WSL: `wsl --shutdown`
3. You can verify that it is shutdown: `wsl.exe --list --verbose`
4. Start diskpart: `diskpart`  
    1. Inside diskpart type: `select vdisk file="<path to vhdx file>"`, for example, `select vdisk file="C:\Users\user\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_12rqwer1sdgsda\LocalState\ext4.vhdx"`
    2. Strink it: `compact vdisk`
    3. If it lets you strink, good, skip to step 6, if not, continue to step 5.
5. If you get a disk part error `The requested operation requires that the virtual disk be attached read only.`:  
    1. Detach the disk: `detach vdisk`
    2. Attach it read only: `attach vdisk readonly`
    3. Run `compact vdisk` again, it should run without issue now.
6. Try starting a WSL terminal. It should work. And check the `.VHDX` file, it should be smaller than before.