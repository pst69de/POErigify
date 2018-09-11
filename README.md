Fork of the original rigify package that is shipped with blender 2.79
============================================================================

## **Be aware that you are using this repository at your own risk !**

## **Do not use alongside with the original Rigify activated !**

After words of warning and you have understand, that this is a developers
version of the original rigify 0.5 that shipped with Blender 2.79 this version
of rigify has caught some interest as it's been made more public by an article
on Lollypopman https://lollypopman.com/2018/09/06/pro-tip-double-controls/.

I'd like to thank Luciano Munoz for this special interest on my toolset.

I mainly use this toolset as an replacement for the original rigify which own functionality is widely left in place so i would expect it to work as the
original, sometimes improved or corrected in one or the other place the original
lacks of precision.

So i did not test, if this toolset may work alongside with the original,
as it is not intended to. And in most cases you would find property panels
being doubled not distinguishable for one or the other. If you experience this
do save your work in a new file, go to user preferences and deactivate both,
rigify and POErigify even if there may be only one selected. Don't forget to
save this preferences and quit Blender. Restart Blender, go to User preferences,
reactivate the one you wish, and save your User Settings again. Then you should
be good to go again.

As with this said, here is a short instruction of how to install and use
POErigify:
* Goto User Preferences (menu File)
* click Add-ons
* in the search type "rigify"
* if your version is active / checked, then uncheck that, and save User Settings,
then quit Blender and start over
* Download the zip-File provided on this page (clone or download, see above) to
your prefered place of Blender Add-ons, if you have none yet, just remember
the place you did save it
* Back in Blender, go to User Preferences, Add-Ons and use Install Addon from
file
* if done, save User Settings to remember the import
* then select Testing in the supported Level, and POErigify should show up,
if not try by typing the name
* check the package and save User Preferences
* then you should be good to go
* if not, restart Blender and doublecheck the Addons in User Preferences as
described

Some features:
* if having a rigify rig (or POErigify ;) ) in Pose mode you'll find a section "POErigify Toolbox" in your Tools panel, having a "Create offset bone WIP" button
i tried some bones in my rigs, that make sense having offset bones and never
failed. But there may be some tricky constellations out, i did not recognize
yet, so i won't give warranties.
* in the tools panel you'll also find a Tool for exporting and importing poses
of a defined rigify rig. The layer matrix selects the bone poses to be exported, every bone will be found in export. Import uses only selected bones to provide the pose to. And it uses the exact name of the exported bone. If you know what you are doing, you can even use this to transfer poses to different rigs, if they share namespaces. But be aware, the stored poses are relative in the exporting rig. So transfering an T pose rig to an A pose rig will give some weird result in the hand positions. Nonetheless this can be a useful start out.
* the Leg bone of the standard metarig has an extra option for foot bending tweaks
* and there a lot of new experimental bone sets, some only for providing a sample set, some with sample and functional "metarig generation", documentation may follow

Feel free and experiment with the opportunities. The code units for the experimental bone sets may also a good source of intuition, as these are not as complex as some of the rigify sets and not that simple as the "super_copy".

If you have questions, problems or ideas, feel free to ask on twitter https://twitter.com/pst69de . This will not be a full service support, as i'm somewhat time limited, but i'll try to help out.

And: if the opportunity comes, i'd be happy to reintegrate some of the features proposed in this package to the original rigify. But i have no contact yet, and some features are that experimental, that they may not make it, be patient.
