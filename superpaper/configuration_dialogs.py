"""
GUI dialogs for Superpaper.
"""
import os

import superpaper.sp_logging as sp_logging
import superpaper.wallpaper_processing as wpproc
from superpaper.data import GeneralSettingsData, ProfileData, TempProfileData, CLIProfileData, list_profiles
from superpaper.message_dialog import show_message_dialog
from superpaper.wallpaper_processing import NUM_DISPLAYS, get_display_data, change_wallpaper_job
from superpaper.sp_paths import PATH, CONFIG_PATH, PROFILES_PATH

try:
    import wx
    import wx.adv
except ImportError:
    exit()



class ProfileConfigFrame(wx.Frame):
    """Profile configuration dialog frame base class."""
    def __init__(self, parent_tray_obj):
        wx.Frame.__init__(self, parent=None, title="Superpaper Profile Configuration")
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        config_panel = ProfileConfigPanel(self, parent_tray_obj)
        self.frame_sizer.Add(config_panel, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.frame_sizer)
        self.Fit()
        self.Layout()
        self.Center()
        self.Show()


class ProfileConfigPanel(wx.Panel):
    """This class defines the config dialog UI."""
    def __init__(self, parent, parent_tray_obj):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.parent_tray_obj = parent_tray_obj
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_left = wx.BoxSizer(wx.VERTICAL) # buttons and prof sel
        self.sizer_right = wx.BoxSizer(wx.VERTICAL) # option fields
        self.sizer_paths = wx.BoxSizer(wx.VERTICAL)
        self.sizer_paths_buttons = wx.BoxSizer(wx.HORIZONTAL)

        self.paths_controls = []

        self.list_of_profiles = list_profiles()
        self.profnames = []
        for prof in self.list_of_profiles:
            self.profnames.append(prof.name)
        self.profnames.append("Create a new profile")
        self.choice_profiles = wx.Choice(self, -1, name="ProfileChoice", choices=self.profnames)
        self.choice_profiles.Bind(wx.EVT_CHOICE, self.onSelect)
        self.sizer_grid_options = wx.GridSizer(5, 4, 5, 5)
        pnl = self
        st_name = wx.StaticText(pnl, -1, "Name")
        st_span = wx.StaticText(pnl, -1, "Spanmode")
        st_slide = wx.StaticText(pnl, -1, "Slideshow")
        st_sort = wx.StaticText(pnl, -1, "Sort")
        st_del = wx.StaticText(pnl, -1, "Delay (600) [sec]")
        st_off = wx.StaticText(pnl, -1, "Offsets (w1,h1;w2,h2) [px]")
        st_in = wx.StaticText(pnl, -1, "Diagonal inches (24.0;13.3) [in]")
        # st_ppi = wx.StaticText(pnl, -1, "PPIs")
        st_bez = wx.StaticText(pnl, -1, "Bezels (10.1;9.5) [mm]")
        st_hk = wx.StaticText(pnl, -1, "Hotkey (control+alt+w)")

        tc_width = 160
        self.tc_name = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        self.ch_span = wx.Choice(pnl, -1, name="SpanChoice",
                                 size=(tc_width, -1),
                                 choices=["Single", "Multi"])
        self.ch_sort = wx.Choice(pnl, -1, name="SortChoice",
                                 size=(tc_width, -1),
                                 choices=["Shuffle", "Alphabetical"])
        self.tc_delay = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        self.tc_offsets = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        self.tc_inches = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        # self.tc_ppis = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        self.tc_bez = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        self.tc_hotkey = wx.TextCtrl(pnl, -1, size=(tc_width, -1))
        self.cb_slideshow = wx.CheckBox(pnl, -1, "")  # Put the title in the left column
        self.sizer_grid_options.AddMany(
            [
                (st_name, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.tc_name, 0, wx.ALIGN_LEFT|wx.ALL),
                (st_span, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.ch_span, 0, wx.ALIGN_LEFT),
                (st_slide, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.cb_slideshow, 0, wx.ALIGN_LEFT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (st_sort, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.ch_sort, 0, wx.ALIGN_LEFT),
                (st_del, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.tc_delay, 0, wx.ALIGN_LEFT),
                (st_off, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.tc_offsets, 0, wx.ALIGN_LEFT),
                (st_in, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.tc_inches, 0, wx.ALIGN_LEFT),
                # (st_ppi, 0, wx.ALIGN_RIGHT),
                # (self.tc_ppis, 0, wx.ALIGN_LEFT),
                (st_bez, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.tc_bez, 0, wx.ALIGN_LEFT),
                (st_hk, 0, wx.ALIGN_RIGHT|wx.ALL|wx.ALIGN_CENTER_VERTICAL),
                (self.tc_hotkey, 0, wx.ALIGN_LEFT),
            ]
        )

        # Paths display
        self.paths_widget_default = self.create_paths_widget()
        self.sizer_paths.Add(self.paths_widget_default, 0, wx.CENTER|wx.ALL, 5)


        # Left column buttons
        self.button_apply = wx.Button(self, label="Apply")
        self.button_new = wx.Button(self, label="New")
        self.button_delete = wx.Button(self, label="Delete")
        self.button_save = wx.Button(self, label="Save")
        self.button_align_test = wx.Button(self, label="Align Test")
        self.button_help = wx.Button(self, label="Help")
        self.button_close = wx.Button(self, label="Close")

        self.button_apply.Bind(wx.EVT_BUTTON, self.onApply)
        self.button_new.Bind(wx.EVT_BUTTON, self.onCreateNewProfile)
        self.button_delete.Bind(wx.EVT_BUTTON, self.onDeleteProfile)
        self.button_save.Bind(wx.EVT_BUTTON, self.onSave)
        self.button_align_test.Bind(wx.EVT_BUTTON, self.onAlignTest)
        self.button_help.Bind(wx.EVT_BUTTON, self.onHelp)
        self.button_close.Bind(wx.EVT_BUTTON, self.onClose)

        # Right column buttons
        self.button_add_paths = wx.Button(self, label="Add path")
        self.button_remove_paths = wx.Button(self, label="Remove path")

        self.button_add_paths.Bind(wx.EVT_BUTTON, self.onAddDisplay)
        self.button_remove_paths.Bind(wx.EVT_BUTTON, self.onRemoveDisplay)

        self.sizer_paths_buttons.Add(self.button_add_paths, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_paths_buttons.Add(self.button_remove_paths, 0, wx.CENTER|wx.ALL, 5)


        # Left add items
        self.sizer_left.Add(self.choice_profiles, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_apply, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_new, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_delete, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_save, 0, wx.CENTER|wx.ALL, 5)
        # self.sizer_left.Add(self.button_settings, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_align_test, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_help, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_left.Add(self.button_close, 0, wx.CENTER|wx.ALL, 5)

        # Right add items
        self.sizer_right.Add(self.sizer_grid_options, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_right.Add(self.sizer_paths, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_right.Add(self.sizer_paths_buttons, 0, wx.CENTER|wx.ALL, 5)

        # Collect items at main sizer
        self.sizer_main.Add(self.sizer_left, 0, wx.CENTER|wx.EXPAND)
        self.sizer_main.Add(self.sizer_right, 0, wx.CENTER|wx.EXPAND)

        self.SetSizer(self.sizer_main)
        self.sizer_main.Fit(parent)

        ### End __init__.

    def update_choiceprofile(self):
        """Reload profile list into the choice box."""
        self.list_of_profiles = list_profiles()
        self.profnames = []
        for prof in self.list_of_profiles:
            self.profnames.append(prof.name)
        self.profnames.append("Create a new profile")
        self.choice_profiles.SetItems(self.profnames)

    def create_paths_widget(self):
        """Creates a path input field on the config dialog."""
        new_paths_widget = wx.BoxSizer(wx.HORIZONTAL)
        static_text = "display" + str(len(self.paths_controls)+1) + "paths"
        st_new_paths = wx.StaticText(self, -1, static_text)
        tc_new_paths = wx.TextCtrl(self, -1, size=(500, -1))
        self.paths_controls.append(tc_new_paths)

        new_paths_widget.Add(st_new_paths, 0, wx.CENTER|wx.ALL, 5)
        new_paths_widget.Add(tc_new_paths, 0, wx.CENTER|wx.ALL|wx.EXPAND, 5)

        button_name = "browse-"+str(len(self.paths_controls)-1)
        button_new_browse = wx.Button(self, label="Browse", name=button_name)
        button_new_browse.Bind(wx.EVT_BUTTON, self.onBrowsePaths)
        new_paths_widget.Add(button_new_browse, 0, wx.CENTER|wx.ALL, 5)

        return new_paths_widget

    # Profile setting displaying functions.
    def populate_fields(self, profile):
        """Populates config dialog fields with data from a profile."""
        self.tc_name.ChangeValue(profile.name)
        self.tc_delay.ChangeValue(str(profile.delay_list[0]))
        self.tc_offsets.ChangeValue(self.show_offset(profile.manual_offsets_useronly))
        show_inch = self.val_list_to_colonstr(profile.inches)
        self.tc_inches.ChangeValue(show_inch)
        show_bez = self.val_list_to_colonstr(profile.bezels)
        self.tc_bez.ChangeValue(show_bez)
        self.tc_hotkey.ChangeValue(self.show_hkbinding(profile.hk_binding))

        # Paths displays: get number to show from profile.
        while len(self.paths_controls) < len(profile.paths_array):
            self.onAddDisplay(wx.EVT_BUTTON)
        while len(self.paths_controls) > len(profile.paths_array):
            self.onRemoveDisplay(wx.EVT_BUTTON)
        for text_field, paths_list in zip(self.paths_controls, profile.paths_array):
            text_field.ChangeValue(self.show_list_paths(paths_list))

        if profile.slideshow:
            self.cb_slideshow.SetValue(True)
        else:
            self.cb_slideshow.SetValue(False)

        if profile.spanmode == "single":
            self.ch_span.SetSelection(0)
        elif profile.spanmode == "multi":
            self.ch_span.SetSelection(1)
        else:
            pass
        if profile.sortmode == "shuffle":
            self.ch_sort.SetSelection(0)
        elif profile.sortmode == "alphabetical":
            self.ch_sort.SetSelection(1)
        else:
            pass

    def val_list_to_colonstr(self, array):
        """Formats a list into a colon separated list."""
        list_strings = []
        if array:
            for item in array:
                list_strings.append(str(item))
            return ";".join(list_strings)
        else:
            return ""

    def show_offset(self, offarray):
        """Format an offset array into the user string formatting."""
        offstr_arr = []
        offstr = ""
        if offarray:
            for offs in offarray:
                offstr_arr.append(str(offs).strip("(").strip(")").replace(" ", ""))
            offstr = ";".join(offstr_arr)
            return offstr
        else:
            return ""

    def show_hkbinding(self, hktuple):
        """Format a hotkey tuple into a '+' separated string."""
        if hktuple:
            hkstring = "+".join(hktuple)
            return hkstring
        else:
            return ""


    # Path display related functions.
    def show_list_paths(self, paths_list):
        """Formats a nested list of paths into a user readable string."""
        # Format a list of paths into the set style of listed paths.
        if paths_list:
            pathsstring = ";".join(paths_list)
            return pathsstring
        else:
            return ""

    def onAddDisplay(self, event):
        """Appends a new display paths widget the the list."""
        new_disp_widget = self.create_paths_widget()
        self.sizer_paths.Add(new_disp_widget, 0, wx.CENTER|wx.ALL, 5)
        self.frame.frame_sizer.Layout()
        self.frame.Fit()

    def onRemoveDisplay(self, event):
        """Removes the last display paths widget."""
        if self.sizer_paths.GetChildren():
            self.sizer_paths.Hide(len(self.paths_controls)-1)
            self.sizer_paths.Remove(len(self.paths_controls)-1)
            del self.paths_controls[-1]
            self.frame.frame_sizer.Layout()
            self.frame.Fit()

    def onBrowsePaths(self, event):
        """Opens the pick paths dialog."""
        dlg = BrowsePaths(None, self, event)
        dlg.ShowModal()


    # Top level button definitions
    def onClose(self, event):
        """Closes the profile config panel."""
        self.frame.Close(True)

    def onSelect(self, event):
        """Acts once a profile is picked in the dropdown menu."""
        event_object = event.GetEventObject()
        if event_object.GetName() == "ProfileChoice":
            item = event.GetSelection()
            if event.GetString() == "Create a new profile":
                self.onCreateNewProfile(event)
            else:
                self.populate_fields(self.list_of_profiles[item])
        else:
            pass

    def onApply(self, event):
        """Applies the currently open profile. Saves it first."""
        saved_file = self.onSave(event)
        print(saved_file)
        if saved_file is not None:
            saved_profile = ProfileData(saved_file)
            self.parent_tray_obj.reload_profiles(event)
            self.parent_tray_obj.start_profile(event, saved_profile)
        else:
            pass

    def onCreateNewProfile(self, event):
        """Empties the config dialog fields."""
        self.choice_profiles.SetSelection(
            self.choice_profiles.FindString("Create a new profile")
            )

        self.tc_name.ChangeValue("")
        self.tc_delay.ChangeValue("")
        self.tc_offsets.ChangeValue("")
        self.tc_inches.ChangeValue("")
        self.tc_bez.ChangeValue("")
        self.tc_hotkey.ChangeValue("")

        # Paths displays: get number to show from profile.
        while len(self.paths_controls) < 1:
            self.onAddDisplay(wx.EVT_BUTTON)
        while len(self.paths_controls) > 1:
            self.onRemoveDisplay(wx.EVT_BUTTON)
        for text_field in self.paths_controls:
            text_field.ChangeValue("")

        self.cb_slideshow.SetValue(False)
        self.ch_span.SetSelection(-1)
        self.ch_sort.SetSelection(-1)

    def onDeleteProfile(self, event):
        """Deletes the currently selected profile after getting confirmation."""
        profname = self.tc_name.GetLineText(0)
        fname = PROFILES_PATH + profname + ".profile"
        file_exists = os.path.isfile(fname)
        if not file_exists:
            msg = "Selected profile is not saved."
            show_message_dialog(msg, "Error")
            return
        # Open confirmation dialog
        dlg = wx.MessageDialog(None,
                               "Do you want to delete profile:"+ profname +"?",
                               'Confirm Delete',
                               wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES and file_exists:
            os.remove(fname)
        else:
            pass

    def onSave(self, event):
        """Saves currently open profile into file. A test method is called to verify data."""
        tmp_profile = TempProfileData()
        tmp_profile.name = self.tc_name.GetLineText(0)
        tmp_profile.spanmode = self.ch_span.GetString(self.ch_span.GetSelection()).lower()
        tmp_profile.slideshow = self.cb_slideshow.GetValue()
        tmp_profile.delay = self.tc_delay.GetLineText(0)
        tmp_profile.sortmode = self.ch_sort.GetString(self.ch_sort.GetSelection()).lower()
        tmp_profile.inches = self.tc_inches.GetLineText(0)
        tmp_profile.manual_offsets = self.tc_offsets.GetLineText(0)
        tmp_profile.bezels = self.tc_bez.GetLineText(0)
        tmp_profile.hk_binding = self.tc_hotkey.GetLineText(0)
        for text_field in self.paths_controls:
            tmp_profile.paths_array.append(text_field.GetLineText(0))

        sp_logging.G_LOGGER.info(tmp_profile.name)
        sp_logging.G_LOGGER.info(tmp_profile.spanmode)
        sp_logging.G_LOGGER.info(tmp_profile.slideshow)
        sp_logging.G_LOGGER.info(tmp_profile.delay)
        sp_logging.G_LOGGER.info(tmp_profile.sortmode)
        sp_logging.G_LOGGER.info(tmp_profile.inches)
        sp_logging.G_LOGGER.info(tmp_profile.manual_offsets)
        sp_logging.G_LOGGER.info(tmp_profile.bezels)
        sp_logging.G_LOGGER.info(tmp_profile.hk_binding)
        sp_logging.G_LOGGER.info(tmp_profile.paths_array)

        if tmp_profile.test_save():
            saved_file = tmp_profile.save()
            self.update_choiceprofile()
            self.parent_tray_obj.reload_profiles(event)
            self.parent_tray_obj.register_hotkeys()
            # self.parent_tray_obj.register_hotkeys()
            self.choice_profiles.SetSelection(self.choice_profiles.FindString(tmp_profile.name))
            return saved_file
        else:
            sp_logging.G_LOGGER.info("test_save failed.")
            return None

    def onAlignTest(self, event):
        """Align test, takes alignment settings from open profile and sets a test image wp."""
        # Use the settings currently written out in the fields!
        testimage = [os.path.join(PATH, "superpaper/resources/test.png")]
        if not os.path.isfile(testimage[0]):
            print(testimage)
            msg = "Test image not found in {}.".format(testimage)
            show_message_dialog(msg, "Error")
        ppi = None
        inches = self.tc_inches.GetLineText(0).split(";")
        if (inches == "") or (len(inches) < NUM_DISPLAYS):
            msg = "You must enter a diagonal inch value for every \
display, serparated by a semicolon ';'."
            show_message_dialog(msg, "Error")

        # print(inches)
        inches = [float(i) for i in inches]
        bezels = self.tc_bez.GetLineText(0).split(";")
        bezels = [float(b) for b in bezels]
        offsets = self.tc_offsets.GetLineText(0).split(";")
        offsets = [[int(i.split(",")[0]), int(i.split(",")[1])] for i in offsets]
        flat_offsets = []
        for off in offsets:
            for pix in off:
                flat_offsets.append(pix)
        # print("flat_offsets= ", flat_offsets)
        # Use the simplified CLI profile class
        get_display_data()
        profile = CLIProfileData(testimage,
                                 ppi,
                                 inches,
                                 bezels,
                                 flat_offsets,
                                )
        change_wallpaper_job(profile)

    def onHelp(self, event):
        """Open help dialog."""
        help_frame = HelpFrame()


class BrowsePaths(wx.Dialog):
    """Path picker dialog class."""
    def __init__(self, parent, show_adv):
        wx.Dialog.__init__(self, parent, -1, 'Choose image source directories or image files', size=(750, 850))
        BMP_SIZE = 32
        self.tsize = (BMP_SIZE, BMP_SIZE)
        self.il = wx.ImageList(BMP_SIZE, BMP_SIZE)

        self.show_adv = show_adv
        self.path_list_data = []
        self.paths = []
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_browse = wx.BoxSizer(wx.VERTICAL)
        self.sizer_paths_list = wx.BoxSizer(wx.VERTICAL)
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.dir3 = wx.GenericDirCtrl(
            self, -1,
            #   size=(450, 550),
            #   style=wx.DIRCTRL_SHOW_FILTERS|wx.DIRCTRL_MULTIPLE,
            #   style=wx.DIRCTRL_MULTIPLE,
            # dir=def_dir,
            filter="Image files (*.jpg, *.png)|*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.webp"
        )
        sizer_browse.Add(self.dir3, 1, wx.CENTER|wx.ALL|wx.EXPAND, 5)
        st_paths_list = wx.StaticText(
            self, -1,
            "Selected wallpaper source directories and files:"
        )
        self.sizer_paths_list.Add(st_paths_list, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.create_paths_listctrl(self.show_adv)

        if self.show_adv:
            sizer_radio = wx.BoxSizer(wx.VERTICAL)
            radio_choices_displays = ["Display {}".format(i) for i in range(wpproc.NUM_DISPLAYS)]
            self.radiobox_displays = wx.RadioBox(self, wx.ID_ANY,
                                                 label="Select display to add sources to",
                                                 choices=radio_choices_displays,
                                                 style=wx.RA_HORIZONTAL
                                                )
            sizer_radio.Add(self.radiobox_displays, 0, wx.CENTER|wx.ALL|wx.EXPAND, 5)


        self.button_add = wx.Button(self, label="Add source")
        self.button_remove = wx.Button(self, label="Remove source")
        self.button_ok = wx.Button(self, label="Ok")
        self.button_cancel = wx.Button(self, label="Cancel")

        self.button_add.Bind(wx.EVT_BUTTON, self.onAdd)
        self.button_remove.Bind(wx.EVT_BUTTON, self.onRemove)
        self.button_ok.Bind(wx.EVT_BUTTON, self.onOk)
        self.button_cancel.Bind(wx.EVT_BUTTON, self.onCancel)

        sizer_buttons.Add(self.button_add, 0, wx.CENTER|wx.ALL, 5)
        sizer_buttons.Add(self.button_remove, 0, wx.CENTER|wx.ALL, 5)
        sizer_buttons.AddStretchSpacer()
        sizer_buttons.Add(self.button_ok, 0, wx.CENTER|wx.ALL, 5)
        sizer_buttons.Add(self.button_cancel, 0, wx.CENTER|wx.ALL, 5)

        sizer_main.Add(sizer_browse, 1, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND)
        sizer_main.Add(self.sizer_paths_list, 0, wx.ALL|wx.ALIGN_CENTER)
        if self.show_adv:
            sizer_main.Add(sizer_radio, 0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND, 5)
        sizer_main.Add(sizer_buttons, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_main)
        self.SetAutoLayout(True)

    def create_paths_listctrl(self, show_adv):
        if show_adv:
            self.paths_listctrl = wx.ListCtrl(self, -1,
                                              size=(740, 200),
                                              style=wx.LC_REPORT
                                              #  | wx.BORDER_SUNKEN
                                              | wx.BORDER_SIMPLE
                                              #  | wx.BORDER_STATIC
                                              #  | wx.BORDER_THEME
                                              #  | wx.BORDER_NONE
                                              #  | wx.LC_EDIT_LABELS
                                              | wx.LC_SORT_ASCENDING
                                              #  | wx.LC_NO_HEADER
                                              #  | wx.LC_VRULES
                                              #  | wx.LC_HRULES
                                              #  | wx.LC_SINGLE_SEL
                                             )
            self.paths_listctrl.InsertColumn(0, 'Display', wx.LIST_FORMAT_RIGHT, width = 100)
            self.paths_listctrl.InsertColumn(1, 'Source', width = 620)
        else:
            # show simpler listing without header if only one wallpaper target
            self.paths_listctrl = wx.ListCtrl(self, -1,
                                              size=(740, 200),
                                              style=wx.LC_REPORT
                                              #  | wx.BORDER_SUNKEN
                                              | wx.BORDER_SIMPLE
                                              #  | wx.BORDER_STATIC
                                              #  | wx.BORDER_THEME
                                              #  | wx.BORDER_NONE
                                              #  | wx.LC_EDIT_LABELS
                                              #  | wx.LC_SORT_ASCENDING
                                              | wx.LC_NO_HEADER
                                              #  | wx.LC_VRULES
                                              #  | wx.LC_HRULES
                                              #  | wx.LC_SINGLE_SEL
                                             )
            self.paths_listctrl.InsertColumn(0, 'Source', width = 720)

        # Add the item list to the control
        self.paths_listctrl.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        self.sizer_paths_list.Add(self.paths_listctrl, 0, wx.CENTER|wx.ALL|wx.EXPAND, 5)

    def append_to_listctrl(self, data_row):
        if self.show_adv:
            img_id = self.add_to_imagelist(data_row[1])
            index = self.paths_listctrl.InsertItem(self.paths_listctrl.GetItemCount(), data_row[0], img_id)
            self.paths_listctrl.SetItem(index, 1, data_row[1])
        else:
            img_id = self.add_to_imagelist(data_row[0])
            index = self.paths_listctrl.InsertItem(self.paths_listctrl.GetItemCount(), data_row[0], img_id)
            # self.paths_listctrl.SetItem(index, 1, data[1])

    def add_to_imagelist(self, path):
        folder_bmp =  wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_TOOLBAR, self.tsize)
        # file_bmp =  wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, self.tsize)
        if os.path.isdir(path):
            img_id = self.il.Add(folder_bmp)
        else:
            thumb_bmp = self.create_thumb_bmp(path)
            img_id = self.il.Add(thumb_bmp)
        return img_id

    def create_thumb_bmp(self, filename):
        wximg = wx.Image(filename, type=wx.BITMAP_TYPE_ANY)
        imgsize = wximg.GetSize()
        w2h_ratio = imgsize[0]/imgsize[1]
        if w2h_ratio > 1:
            target_w = self.tsize[0]
            target_h = target_w/w2h_ratio
            pos = (0, round((target_w - target_h)/2))
        else:
            target_h = self.tsize[1]
            target_w = target_h*w2h_ratio
            pos = (round((target_h - target_w)/2), 0)
        bmp = wximg.Scale(target_w, target_h).Resize(self.tsize, pos).ConvertToBitmap()
        return bmp

    def onAdd(self, event):
        """Adds selected path to export field."""
        path_data_tuples = []
        sel_path = self.dir3.GetPath()
        # self.dir3.GetPaths(paths) # could use this to be more efficient but it does not will the list
        if self.show_adv:
            # Extra column in advanced mode
            disp_id = str(self.radiobox_displays.GetSelection())
            self.append_to_listctrl([disp_id, sel_path])
        else:
            self.append_to_listctrl([sel_path])

    def onRemove(self, event):
        """Removes last appended path from export field."""
        # TODO remove btn should be disabled if not in valid selection
        item = self.paths_listctrl.GetFocusedItem()
        if item != -1:
            self.paths_listctrl.DeleteItem(item)



    def onOk(self, event):
        """Exports path to parent Profile Config dialog."""
        columns = self.paths_listctrl.GetColumnCount()
        for idx in range(self.paths_listctrl.GetItemCount()):
            item_dat = []
            for col in range(columns):
                item_dat.append(self.paths_listctrl.GetItemText(idx, col))
            self.path_list_data.append(item_dat)
        print(self.path_list_data)
        # if listctrl is empty, onOk maybe could pass on the selected item? or disable OK if list is empty?
        self.EndModal(wx.ID_OK)


    def onCancel(self, event):
        """Closes path picker, throwing away selections."""
        self.Destroy()



class SettingsFrame(wx.Frame):
    """Settings dialog frame."""
    def __init__(self, parent_tray_obj):
        wx.Frame.__init__(self, parent=None, title="Superpaper General Settings")
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        settings_panel = SettingsPanel(self, parent_tray_obj)
        self.frame_sizer.Add(settings_panel, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.frame_sizer)
        self.Fit()
        self.Layout()
        self.Center()
        self.Show()

class SettingsPanel(wx.Panel):
    """Settings dialog contents."""
    def __init__(self, parent, parent_tray_obj):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.parent_tray_obj = parent_tray_obj
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.sizer_grid_settings = wx.GridSizer(5, 2, 5, 5)
        self.sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        pnl = self
        st_logging = wx.StaticText(pnl, -1, "Logging")
        st_usehotkeys = wx.StaticText(pnl, -1, "Use hotkeys")
        st_hk_next = wx.StaticText(pnl, -1, "Hotkey: Next wallpaper")
        st_hk_pause = wx.StaticText(pnl, -1, "Hotkey: Pause slideshow")
        st_setcmd = wx.StaticText(pnl, -1, "Custom command")
        self.cb_logging = wx.CheckBox(pnl, -1, "")
        self.cb_usehotkeys = wx.CheckBox(pnl, -1, "")
        self.tc_hk_next = wx.TextCtrl(pnl, -1, size=(200, -1))
        self.tc_hk_pause = wx.TextCtrl(pnl, -1, size=(200, -1))
        self.tc_setcmd = wx.TextCtrl(pnl, -1, size=(200, -1))

        self.sizer_grid_settings.AddMany(
            [
                (st_logging, 0, wx.ALIGN_RIGHT),
                (self.cb_logging, 0, wx.ALIGN_LEFT),
                (st_usehotkeys, 0, wx.ALIGN_RIGHT),
                (self.cb_usehotkeys, 0, wx.ALIGN_LEFT),
                (st_hk_next, 0, wx.ALIGN_RIGHT),
                (self.tc_hk_next, 0, wx.ALIGN_LEFT),
                (st_hk_pause, 0, wx.ALIGN_RIGHT),
                (self.tc_hk_pause, 0, wx.ALIGN_LEFT),
                (st_setcmd, 0, wx.ALIGN_RIGHT),
                (self.tc_setcmd, 0, wx.ALIGN_LEFT),
            ]
        )
        self.update_fields()
        self.button_save = wx.Button(self, label="Save")
        self.button_close = wx.Button(self, label="Close")
        self.button_save.Bind(wx.EVT_BUTTON, self.onSave)
        self.button_close.Bind(wx.EVT_BUTTON, self.onClose)
        self.sizer_buttons.Add(self.button_save, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_buttons.Add(self.button_close, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_main.Add(self.sizer_grid_settings, 0, wx.CENTER|wx.EXPAND)
        self.sizer_main.Add(self.sizer_buttons, 0, wx.CENTER|wx.EXPAND)
        self.SetSizer(self.sizer_main)
        self.sizer_main.Fit(parent)

    def update_fields(self):
        """Updates dialog field contents."""
        g_settings = GeneralSettingsData()
        self.cb_logging.SetValue(g_settings.logging)
        self.cb_usehotkeys.SetValue(g_settings.use_hotkeys)
        self.tc_hk_next.ChangeValue(self.show_hkbinding(g_settings.hk_binding_next))
        self.tc_hk_pause.ChangeValue(self.show_hkbinding(g_settings.hk_binding_pause))
        self.tc_setcmd.ChangeValue(g_settings.set_command)

    def show_hkbinding(self, hktuple):
        """Formats hotkey tuple as a readable string."""
        hkstring = "+".join(hktuple)
        return hkstring

    def onSave(self, event):
        """Saves settings to file."""
        current_settings = GeneralSettingsData()
        show_help = current_settings.show_help

        fname = os.path.join(CONFIG_PATH, "general_settings")
        general_settings_file = open(fname, "w")
        if self.cb_logging.GetValue():
            general_settings_file.write("logging=true\n")
        else:
            general_settings_file.write("logging=false\n")
        if self.cb_usehotkeys.GetValue():
            general_settings_file.write("use hotkeys=true\n")
        else:
            general_settings_file.write("use hotkeys=false\n")
        general_settings_file.write("next wallpaper hotkey="
                                    + self.tc_hk_next.GetLineText(0) + "\n")
        general_settings_file.write("pause wallpaper hotkey="
                                    + self.tc_hk_pause.GetLineText(0) + "\n")
        if show_help:
            general_settings_file.write("show_help_at_start=true\n")
        else:
            general_settings_file.write("show_help_at_start=false\n")
        general_settings_file.write("set_command=" + self.tc_setcmd.GetLineText(0))
        general_settings_file.close()
        # after saving file apply in tray object
        self.parent_tray_obj.read_general_settings()

    def onClose(self, event):
        """Closes settings panel."""
        self.frame.Close(True)


class HelpFrame(wx.Frame):
    """Help dialog frame."""
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="Superpaper Help")
        self.frame_sizer = wx.BoxSizer(wx.VERTICAL)
        help_panel = HelpPanel(self)
        self.frame_sizer.Add(help_panel, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(self.frame_sizer)
        self.Fit()
        self.Layout()
        self.Center()
        self.Show()

class HelpPanel(wx.Panel):
    """Help dialog contents."""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        self.sizer_helpcontent = wx.BoxSizer(wx.VERTICAL)
        self.sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)

        current_settings = GeneralSettingsData()
        show_help = current_settings.show_help

        st_show_at_start = wx.StaticText(self, -1, "Show this help at start")
        self.cb_show_at_start = wx.CheckBox(self, -1, "")
        self.cb_show_at_start.SetValue(show_help)
        self.button_close = wx.Button(self, label="Close")
        self.button_close.Bind(wx.EVT_BUTTON, self.onClose)
        self.sizer_buttons.Add(st_show_at_start, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_buttons.Add(self.cb_show_at_start, 0, wx.CENTER|wx.ALL, 5)
        self.sizer_buttons.Add(self.button_close, 0, wx.CENTER|wx.ALL, 5)

        help_str = """
How to use Superpaper:

In the Profile Configuration you can adjust all your wallpaper settings.
Only required options are name and wallpaper paths. Other application
wide settings can be changed in the Settings menu. Both are accessible
from the system tray menu.

IMPORTANT NOTE: For the wallpapers to be set correctly, you must set
in your OS the background fitting option to 'Span'.

NOTE: If your displays are not in a horizontal row, the pixel density
and offset corrections unfortunately do not work. In this case leave
the 'Diagonal inches', 'Offsets' and 'Bezels' fields empty.

Description of Profile Configuration options:
In the text field description an example is shown in parantheses and in
brackets the expected units of numerical values.

"Diagonal inches": The diagonal diameters of your monitors in
                                order starting from the left most monitor.
                                These affect the wallpaper only in "Single"
                                spanmode.

"Spanmode": "Single" (span a single image across all monitors)
                    "Multi" (set a different image on every monitor.)

"Sort":  Applies to slideshow mode wallpaper order.

"Offsets":  Wallpaper alignment correction offsets for your displays
                if using "Single" spanmode. Entered as "width,height"
                pixel value pairs, pairs separated by a semicolon ";".
                Positive offsets move the portion of the image on 
                the monitor down and to the right, negative offets
                up or left.

"Bezels":   Bezel correction for "Single" spanmode wallpaper. Use this
                if you want the image to continue behind the bezels,
                like a scenery does behind a window frame. The expected
                values are the combined widths in millimeters of the
                two adjacent monitor bezels including a possible gap.

"Hotkey":   An optional key combination to apply/start the profile.
                Supports up to 3 modifiers and a key. Valid modifiers
                are 'control', 'super', 'alt' and 'shift'. Separate
                keys with a '+', like 'control+alt+w'.

"display{N}paths":  Wallpaper folder paths for the display in the Nth
                        position from the left. Multiple can be entered with
                        the browse tool using "Add". If you have more than
                        one vertically stacked row, they should be listed
                        row by row starting from the top most row.

Tips:
- You can use the given example profiles as templates: just change
    the name and whatever else, save, and its a new profile.
- 'Align Test' feature allows you to test your offset and bezel settings.
    Display diagonals, offsets and bezels need to be entered.
"""
        st_help = wx.StaticText(self, -1, help_str)
        self.sizer_helpcontent.Add(st_help, 0, wx.EXPAND|wx.CENTER|wx.ALL, 5)

        self.sizer_main.Add(self.sizer_helpcontent, 0, wx.CENTER|wx.EXPAND)
        self.sizer_main.Add(self.sizer_buttons, 0, wx.CENTER|wx.EXPAND)
        self.SetSizer(self.sizer_main)
        self.sizer_main.Fit(parent)

    def onClose(self, event):
        """Closes help dialog. Saves checkbox state as needed."""
        if self.cb_show_at_start.GetValue() is True:
            current_settings = GeneralSettingsData()
            if current_settings.show_help is False:
                current_settings.show_help = True
                current_settings.save_settings()
        else:
            # Save that the help at start is not wanted.
            current_settings = GeneralSettingsData()
            show_help = current_settings.show_help
            if show_help:
                current_settings.show_help = False
                current_settings.save_settings()
        self.frame.Close(True)
