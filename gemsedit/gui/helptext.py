# "this <b>bold</b> and <i>italics</i> out"

condition_desc = {
    "": "<b>Blank</b> : Returns a blank condition.",
    "VarValueIs": "<b>VarValueIs</b>(Variable,Value) : This condition returns <i>true</i> if the user-created token <b><i>Variable</i></b> exists and currently has the value <b><i>Value</i></b>.",
    "VarValueIsNot": "<b>VarValueIsNot</b>(Variable,Value) : This condition returns <i>true</i> if the user-created token <b><i>Variable</i></b> currently <u>does not have</u> the value <b><i>Value</i></b> or does not exist.",
    "VarExists": "<b>VarExists</b>(Variable) : This condition returns <i>true</i> if the user-created token <b><i>Variable</i></b> currently exists.",
    "ViewTimePassed": "<b>ViewTimePassed</b>(Seconds) : This condition returns <i>true</i> if at least <b><i>Seconds</i></b> seconds has passed since the current view was displayed.",
    "TotalTimePassed": "<b>TotalTimePassed</b>(Seconds) : This condition returns <i>true</i> if at least <b><i>Seconds</i></b> seconds has passed since the current GEMS environment was started.",
    "VarCountEq": "<b>VarCountEq</b>(Count) : This condition returns <i>true</i> if the number of user-created variables <u>equals</u> <b><i>Count</i></b>.",
    "VarCountGtEq": "<b>VarCountGtEq</b>(Count) : This condition returns <i>true</i> if the number of user-created variables is <u>greater than or equal to</u> <b><i>Count</i></b>.",
    "VarCountLtEq": "<b>VarCountLtEq</b>(Count) : This condition returns <i>true</i> if the number of user-created variables is <u>less than or equal to</u> <b><i>Count</i></b>.",
    "KeyBufferContains": "<b>KeyBufferContains</b>(String,IgnoreCase) : This condition returns <i>true</i> when the keyboard buffer contains the characters in <b><i>Keys</i></b>. Use only these characters: \[a-zA-Z0-9 -_./\]. Optionally set <b>IgnoreCase</b> to True (default is False). It is recommended that the action ClearKeyBuffer() precede use of this condition. You can Optionally set <b>IgnoreCase</b> to True(default is False).",
}

trigger_desc = {
    "": "<b>Blank</b> : Returns a blank trigger.",
    "ViewTimePassed": "<b>ViewTimePassed</b>(Seconds) : This trigger fires when at least <b><i>Seconds</i></b> seconds has passed since the current view was displayed.",
    "TotalTimePassed": "<b>TotalTimePassed</b>(Seconds) : This trigger fires when at least <b><i>Seconds</i></b> seconds has passed since the current GEMS environment was started.",
    "MouseClick": "<b>MouseClick</b>() : This trigger fires whenever the mouse is <i>left</i>-clicked.",
    "DroppedOn": "<b>DroppedOn</b>(Object) : This trigger fires when <b><i>Object</i></b> is dragged and then dropped onto the associated object.",
    "KeyPress": "<b>KeyPress</b>(Key) : This trigger fires when <b><i>Key</i></b> is entered on the keyboard.",
    "NavLeft": "<b>NavLeft</b>() : This trigger fires whenever the mouse is <i>left</i>-clicked towards the <b><i>Left</i></b> edge of the screen.",
    "NavRight": "<b>NavRight</b>() : This trigger fires whenever the mouse is <i>left</i>-clicked towards the <b><i>Right</i></b> edge of the screen.",
    "NavTop": "<b>NavTop</b>() : This trigger fires whenever the mouse is <i>left</i>-clicked towards the <b><i>Top</i></b> edge of the screen.",
    "NavBottom": "<b>NavBottom</b>() : This trigger fires whenever the mouse is <i>left</i>-clicked towards the <b><i>Bottom</i></b> edge of the screen.",
}

action_desc = {
    "": "<b>Blank</b> : Returns a blank action.",
    "PortalTo": "<b>PortalTo</b>(View) : This action causes GEMS to load <b><i>View</i></b>.",
    "PlaySound": '<b>PlaySound</b>(SoundFile,Start,Volume,Loop) : This action instructs GEMS to play the audio in <b><i>SoundFile</i></b>. The soundfile beings playing at <b><i>Start</i></b> seconds \[Default = 0 = beginning\] and plays at the desired <b><i>Volume</i></b> \[0.0 to 1.0\]. If <b><i>Loop</i></b> is "True" \[default = "False"\], the soundfile will loop continually.',
    "PlayVideo": "<b>PlayVideo</b>(VideoFile,Start,Left,Top,WithinObject) : This action instructs GEMS to play the video in <b><i>VideoFile</i></b> at position (<b><i>Left</i></b>,<b><i>Top</i></b>). The videofile beings playing at <b><i>Start</i></b> seconds \[Default = 0 = beginning\]. If <b><i>WithinObject</i></b> refers to a currently visible object, the video will play within that object's boundary. Otherwise, the video will play fullscreen.",
    "ShowImage": '<b>ShowImage</b>(ImageFile,Left,Top,Duration,Clickthrough) : This action loads and displays <b><i>ImageFile</i></b> at (Left,Top) for <b><i>Duration</i></b> seconds \[default = 0 = forever\]. The image is removed when the view is changed. If <b><i>Clickthrough</i></b> is "True" \[default = "False"\], clickable objects <em>under</em> the image will continue to fire associated actions.',
    "RunProgram": "<b>RunProgram</b>(Application,Parameters) : This action causes GEMS to execute <b><i>Application</i></b> with any provided optional <b><i>Parameters</i></b>.",

    # TODO: Add volume parameter to SayText vvv
    "SayText": "<b>SayText</b>(Message) : This action causes GEMS to speak aloud the given <b><i>Message</i></b> using the default text-to-speech voice.",

    # TODO: Consider using this approach vvv for describing pixel position in other descriptions.
    #       Alternatively, put this verbiage in the hovertext for the left/top input boxes
    "TextBox": "<b>TextBox</b>(Message,Left,Top,Duration,FontColor) : This action causes GEMS to draw a textbox over the current view containing the text in <b><i>Message</i></b>. The message will be positioned at <b><i>Left</i></b> pixels from the left and <b><i>Top</i></b> pixels from the top of the view. After <b><i>Duration</i></b> seconds \[default = 0 = forever\], the textbox will be removed. Set <b><i>FontColor</i></b> as desired. if left,top is (-1, -1), message origin will be current mouse position.",
    "TextDialog": "<b>TextDialog</b>(Message) : This action causes GEMS to display an input dialog box containing <b><i>Message</i></b>. The dialog box will remain until the user presses the SUBMIT button.",
    "InputDialog": "<b>InputDialog</b>(Prompt,Variable) : This action causes GEMS to display an input dialog box containing the query <b><i>Prompt</i></b>. The dialog box will remain until the user presses the SUBMIT button. The entered text will be associated with the user variable <b><i>Variable</i></b>",
    "ShowURL": "<b>ShowURL</b>(URL) : This action shows a custom browser window and loads the page at the supplied <b><i>URL</i></b>. The window remains atop the GEMS environment until dismissed by the user (close button).",
    "HideObject": "<b>HideObject</b>(Object) : This action causes the object identified as <b><i>Object</i></b> invisible.",
    "ShowObject": "<b>ShowObject</b>(Object) : This action causes the object identified as <b><i>Object</i></b> visible.",
    "AllowTake": "<b>AllowTake</b>(Object) : This action sets the <i>Takeable</i> property on the object identified as <b><i>Object</i></b>.",
    "DisallowTake": "<b>DisallowTake</b>(Object) : This action sets the <i>Takeable</i> property of the object identified as <b><i>Object</i></b>.",

    # TODO: This doesn't get exposed anywhere vvv, is it supposed to?
    "ChangeCursor": "<b>ChangeCursor</b>(Cursor) : This action causes GEMS to change the mouse cursor to <b><i>Cursor</i></b>.",
    "SetVariable": "<b>SetVariable</b>(Variable,Value) : This action sets the user-created token <b><i>Variable</i></b> to <b><i>Value</i></b>. If <b><i>Variable</i></b> does not exist, it will be created first.",
    "DelVariable": "<b>DelVariable</b>(Variable) : This action removes the user-created token <b><i>Variable</i></b>.",
    "ClearKeyBuffer": "<b>ClearKeyBuffer</b>() : This action clears all characters in the keyboard buffer.",
    "Quit": "<b>Quit</b>() : This action terminates the current GEMS environment.",
    "HideMouse": "<b>HideMouse</b>() : This action hides the mouse cursor.",
    "ShowMouse": "<b>ShowMouse</b>() : This action unhides the mouse cursor.",
    "HidePockets": "<b>HidePockets</b>() : This action hides all active pockets.",
    "ShowPockets": "<b>ShowPockets</b>() : This action unhides all active pockets.",
}

# (Id INT PRIMARY KEY UNIQUE, Startview INT, Pocketcount INT,
# Roomtrasition TEXT, Preloadresources INT, Globaloverlay TEXT, Version REAL)

# settings_desc = {
#     'Id': '',
#     'Startview': '<b>Starting View</b> : When run, the GEMS environment with first open this view.',
#     'Pocketcount': '<b>Pocket Count</b> : Number of pockets to display/use in the environment.',
#     'Roomtransition': '<b>Room Transition</b> : Dictates how images will transition between views.',
#     'Preloadresources': '<b>Preload Resources</b> : Preload all resources into RAM before starting environment.',
#     'Globaloverlay': '<b>Global Overly</b> : Overlay to use on all views unless overidden by overlays on
#     individual views.',
#     'Version': '',
# }

# NOTE: These are being indexed by the setting_item value which differs from scheme used for other keys in this module!
#       feb 10 2022 -tls
settings_desc = {
    "Id": "",
    "Start View": "<b>Starting View</b> : When run, the GEMS environment with first open this view.",
    "Pocket Count": "<b>Pocket Count</b> : Number of pockets to display/use in the environment.",
    "View Transition": "<b>Room Transition</b> : Dictates how images will transition between views.",
    "Preload Resources": "<b>Preload Resources</b> : Preload all resources into RAM before starting environment."
    " Currently limited to pre-generating Text-To-Speech outputs.",
    "Global Overlay\n(Right-Click To Clear)": "<b>Global Overly</b> : Overlay to use on all views unless overridden "
    "by overlays on individual views.",
    "GEMSedit Version": "<b>GEMSedit Version</b> : GEMSrun version with which the environment database was last saved. "
    "NOTE: This setting updates automatically and is not user editable.",
    "Stage Color": "<b>Stage Color</b> : Background color of main window within GEMSrun. Will only be visible if "
    "image size < screen size. It could possibly be visible during view changes on slower computers.",
    "Display Type": "<b>Display Type</b> : Either Windowed (GEMSrun sizes its main window to the image size) or "
    "FullScreen (GEMSrun sets its main window to full screen mode).",
    "Object Hover": "<b>Object Hover</b> : Indicates what (if any) information GEMSrun gives users when the mouse "
    "cursor hovers over an object. The default is a subtle change in the mouse cursor. There are "
    "several less subtle options, mostly used in debugging. You can also choose to do nothing when"
    "objects are hovered -- this may be confusing to users and is not recommended.",
    "Media Volume": "This settings sets the overall volume level for any media playback within GEMSrun (0.0 to 1.0).",
}

transistion_desc = {
    "None": "<b>None</b> : No transition.",
    "Fade": "<b>Fade</b> : Fade transition.",
}

# ObjectHover TEXT (none,frameobject, cursorchange, tooltip)
# helptext.hover_desc

display_desc = {
    "Windowed": "<b>Windowed</b> : Each view\'s image is viewed in an application window of the same size.",
    "Fullscreen": "<b>Stretch</b> : GEMS is run in fullscreen mode, with each view\'s image stretched to fill "
                  "the screen.",
}

hover_desc = {
    "None": "<b>None</b> : No effect when hovering above objects.",
    "ChangeCursor": "<b>ChangeCursor</b> : When hovering above objects, the object's cursor is changed to a yellow hand.",
    "FrameObject": "<b>FrameObject</b> : When hovering above objects, the object's boundary rectangle becomes visible.",
    "ShowName": "<b>ShowName</b> : When hovering above objects, the object's name is displayed near the object image.",
    "Frame+Cursor": "<b>Frame+Cursor</b> : Combines ChangeCursor and FrameObject behaviors.",
    "Name+Cursor": "<b>Name+Cursor</b> : Combines ShowName and ChangeCursor behaviors.",
    "Frame+Name": "<b>Frame+Name</b> : Combines ShowName and FrameObject behaviors.",
    "Cursor+Frame+Name": "<b>Cursor+Frame+Name</b> : Combines ShowName and FrameObject and ChangeCursor behaviors.",
}
