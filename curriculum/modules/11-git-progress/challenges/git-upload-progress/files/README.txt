Upload Progress With Git
========================

Everyday solving
----------------
You do **not** need to push by hand after each clear. On first startup the lab
created academy-progress.git and keeps updating progress/<you> for you.

When you want a backup / share (USB or GitHub)
---------------------------------------------
Same idea as this practice:

1. Have an empty git repository ready (folder or GitHub URL).
2. Point the lab at it:
     academy progress remote https://github.com/ORG/academy-progress.git
3. Upload every student branch:
     academy progress push

Or in Admin → Progress sync → Save remote → Push all branches.

This challenge (offline practice)
---------------------------------
1. Press Start.
2. Run:  ./practice_upload
   It makes practice-remote.git here and pushes your branch into it.
3. When you see UPLOAD_OK, run:  ./check
4. Press Done.
