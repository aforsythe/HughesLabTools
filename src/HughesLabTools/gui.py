from __future__ import print_function, division, absolute_import
from ij import IJ, gui

class VmoToolsGui:
    """
    A GUI class for collecting user input to configure and run VMO tools.

    Attributes:
        options (dict): A dictionary storing various operational options selected by the user.
        num_types (int): The number of image types selected by the user.
    """

    def __init__(self):
        """Initializes an empty options dictionary and sets num_types to None."""
        self.options = {}
        self.num_types = None
        self.type_names = []
        self.type_colors = []

    def show_gui(self, device_manager=None):
        """
        Displays the GUI to collect options and configure the DeviceManager.

        Args:
            device_manager (DeviceManager, optional): An instance of DeviceManager to configure. Defaults to None.

        Returns:
            dict or DeviceManager: Returns the options dictionary if device_manager is not provided;
                                   otherwise, returns the configured DeviceManager instance.
        """
        if not self._collect_function_options():
            return None

        if not self._collect_number_of_image_types():
            return None

        if not self._collect_additional_options():
            return None

        if not self._collect_root_directory():
            return None  # Stop if the user cancels the directory selection

        if device_manager:
            # Configure the device manager with numTypes, typeNames, and typeColors as attributes
            self._configure_device_manager(device_manager)
            return device_manager

        # Store numTypes, typeNames, and typeColors in the options dictionary
        self.options['numTypes'] = self.num_types
        self.options['typeNames'] = self.type_names
        self.options['typeColors'] = self.type_colors

        return self.options

    def _collect_function_options(self):
        """
        Collects the main function options from the user through a dialog.

        Returns:
            bool: True if the dialog is not canceled, False otherwise.
        """
        dialog = gui.GenericDialog('Run VMO Tools')
        radio_buttons = ['Color and Merge Images', 'Color Images', 'No Coloring']
        dialog.addRadioButtonGroup('Image Coloring Tools:', radio_buttons, 3, 1, radio_buttons[0])

        dialog.setInsets(15, 10, 0)
        dialog.addMessage('Tumor Image Tools:')
        tumor_checkbox_labels = ['Segment Tumor Images', 'Measure Tumor Grey Level', 'Measure Tumor Circularity']
        dialog.addCheckboxGroup(3, 1, tumor_checkbox_labels, [False] * 3)

        dialog.setInsets(15, 10, 0)
        dialog.addMessage('Vessel Image Tools:')
        vessel_checkbox_labels = ['Threshold Vessel Images', 'Measure Vessel Diameter']
        dialog.addCheckboxGroup(2, 1, vessel_checkbox_labels, [False] * 2)

        dialog.setOKLabel('Next ...')
        dialog.showDialog()

        if dialog.wasCanceled():
            return False

        self._parse_function_options(dialog, radio_buttons)
        return True

    def _parse_function_options(self, dialog, radio_buttons):
        """
        Parses the function options selected by the user and stores them in the options dictionary.

        Args:
            dialog (GenericDialog): The dialog instance containing user selections.
            radio_buttons (list): A list of radio button labels for image coloring options.
        """
        selected_option = dialog.getNextRadioButton()
        self.options['color'], self.options['merge'] = self._parse_color_merge_option(selected_option, radio_buttons)
        self.options['segment'] = dialog.getNextBoolean()
        self.options['meas_grey'] = dialog.getNextBoolean()
        self.options['meas_circ'] = dialog.getNextBoolean()
        self.options['threshold'] = dialog.getNextBoolean()
        self.options['meas_diam'] = dialog.getNextBoolean()

    def _parse_color_merge_option(self, selected_option, radio_buttons):
        """
        Helper function to parse the color and merge options.

        Args:
            selected_option (str): The selected radio button option.
            radio_buttons (list): A list of radio button labels for image coloring options.

        Returns:
            tuple: A tuple containing two booleans, indicating whether to color and merge images.
        """
        if selected_option == radio_buttons[0]:
            return True, True
        elif selected_option == radio_buttons[1]:
            return True, False
        else:
            return False, False

    def _collect_number_of_image_types(self):
        """
        Collects the number of image types the user wants to process.

        Returns:
            bool: True if the dialog is not canceled, False otherwise.
        """
        dialog = gui.GenericDialog('Number of Image Types')
        if self.options['color']:
            dialog.addMessage('How many image types are you processing?')
        else:
            dialog.addMessage('How many image types are in the directories you are processing?')

        dialog.addMessage('Examples:\nVessels and Tumors = 2\nVessels, Tumors, and Fibroblasts = 3')
        dialog.setInsets(5, 60, 5)

        dialog.addChoice('', [str(x + 1) for x in range(6)], '2')

        dialog.setOKLabel('Next ...')
        dialog.showDialog()

        if dialog.wasCanceled():
            return False

        self.num_types = int(dialog.getNextChoice())  # Store numTypes separately
        return True

    def _collect_additional_options(self):
        """
        Collects additional options such as image type names and colors.

        Returns:
            bool: True if the dialog is not canceled, False otherwise.
        """
        dialog = gui.GenericDialog('Image Type Names and Colors')
        possible_colors = ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow']
        default_names = ['Vessels', 'Tumor', 'Fibroblasts', 'Cell 1', 'Cell 2', 'Cell 3']

        type_names, type_colors = [], []

        for i in range(self.num_types):
            dialog.addMessage('Image Type: ' + str(i + 1))
            dialog.setInsets(5, 20, 0)
            if self.options['color']:
                dialog.addChoice('Color:', possible_colors, possible_colors[i])
                dialog.addToSameRow()
            dialog.addStringField('Name:', default_names[i], 10)

        self._add_optional_dialog_sections(dialog)

        dialog.setOKLabel('Next ...')
        dialog.showDialog()

        if dialog.wasCanceled():
            return False

        for i in range(self.num_types):
            type_names.append(dialog.getNextString())
            type_colors.append(dialog.getNextChoice())

        # Store these directly in the DeviceManager (or wherever you want to store them)
        self.type_names = type_names
        self.type_colors = type_colors

        self._finalize_additional_options(dialog)
        return True

    def _add_optional_dialog_sections(self, dialog):
        """
        Adds optional sections to the dialog based on previous choices.

        Args:
            dialog (GenericDialog): The dialog instance where additional sections will be added.
        """
        if self.options['color']:
            self._add_color_merge_options(dialog)
        if self.options['segment']:
            self._add_segment_options(dialog)
        if self.options['threshold']:
            self._add_threshold_options(dialog)
        if self.options['meas_diam']:
            self._add_measure_diameter_options(dialog)
        if self.options['meas_circ']:
            self._add_circularity_options(dialog)

        self._add_file_options(dialog)

    def _add_color_merge_options(self, dialog):
        """
        Adds color and merge options to the dialog.

        Args:
            dialog (GenericDialog): The dialog instance where the color and merge options will be added.
        """
        dialog.setInsets(25, 20, 0)
        dialog.addMessage('Color and Merge Options:')
        dialog.setInsets(5, 25, 0)
        dialog.addCheckbox('Show colored images', self.options.get('show_colored', False))
        dialog.addToSameRow()
        dialog.addNumericField('Sat level:', 0.3, 2)
        if self.options['merge']:
            dialog.setInsets(5, 25, 0)
            dialog.addCheckbox('Show merged images', self.options.get('show_merged', False))

    def _add_segment_options(self, dialog):
        """
        Adds segment options to the dialog.

        Args:
            dialog (GenericDialog): The dialog instance where the segment options will be added.
        """
        dialog.setInsets(25, 20, 0)
        dialog.addMessage('Segment Tumor Options:')
        dialog.setInsets(5, 25, 0)
        dialog.addCheckbox('Show segmented images', False)

    def _add_threshold_options(self, dialog):
        """
        Adds threshold options to the dialog.

        Args:
            dialog (GenericDialog): The dialog instance where the threshold options will be added.
        """
        dialog.setInsets(25, 20, 0)
        dialog.addMessage('Threshold Vessel Image Options:')
        dialog.setInsets(5, 25, 0)
        dialog.addCheckbox('Show thresholded images', False)

    def _add_measure_diameter_options(self, dialog):
        """
        Adds measure diameter options to the dialog.

        Args:
            dialog (GenericDialog): The dialog instance where the measure diameter options will be added.
        """
        dialog.setInsets(25, 20, 0)
        dialog.addMessage('Vessel Measurement Options:')
        dialog.setInsets(5, 25, 0)
        dialog.addCheckbox('Show settings for each image', False)

    def _add_circularity_options(self, dialog):
        """
        Adds circularity options to the dialog.

        Args:
            dialog (GenericDialog): The dialog instance where the circularity options will be added.
        """
        dialog.setInsets(25, 20, 0)
        dialog.addMessage('Circularity Measurement Options:')
        dialog.setInsets(5, 25, 0)
        dialog.addNumericField("Black", 0, 0)
        dialog.addNumericField("Min Size", 50, 0)
        dialog.addNumericField("Max Size", 10000, 0)

    def _add_file_options(self, dialog):
        """
        Adds file processing options to the dialog.

        Args:
            dialog (GenericDialog): The dialog instance where the file options will be added.
        """
        dialog.setInsets(25, 20, 0)
        dialog.addMessage('File Options:')
        dialog.setInsets(5, 25, 0)
        dialog.addCheckbox('Process images in subdirectories', self.options.get('process_subdirectories', True))
        dialog.addToSameRow()
        dialog.addCheckbox('Confirm image types', self.options.get('confirm_image_types', False))
        dialog.setInsets(5, 25, 0)
        dialog.addCheckbox('Verbose Logging', self.options.get('verbose', False))

    def _finalize_additional_options(self, dialog):
        """
        Finalizes the additional options collected from the user.

        Args:
            dialog (GenericDialog): The dialog instance from which final options are retrieved.
        """
        if self.options['color']:
            self.options['show_colored'] = dialog.getNextBoolean()
            self.options['sat'] = dialog.getNextNumber()
        if self.options['merge']:
            self.options['show_merged'] = dialog.getNextBoolean()
        if self.options['segment']:
            self.options['show_segmented'] = dialog.getNextBoolean()
        if self.options['threshold']:
            self.options['show_threshold'] = dialog.getNextBoolean()
        if self.options['meas_diam']:
            self.options['vessel_settings'] = dialog.getNextBoolean()
        if self.options['meas_circ']:
            self.options['circ_bp'] = dialog.getNextNumber()
            self.options['circ_st'] = dialog.getNextNumber()
            self.options['circ_lt'] = dialog.getNextNumber()

        # Only store operational options in self.options
        self.options['process_subdirectories'] = dialog.getNextBoolean()
        self.options['confirm_image_types'] = dialog.getNextBoolean()
        self.options['verbose'] = dialog.getNextBoolean()

    def _collect_root_directory(self):
        """
        Prompts the user to select the root directory and stores it in options.

        Returns:
            bool: True if a root directory is selected, False otherwise.
        """
        self.options['rootDir'] = IJ.getDirectory("Select Root Directory")
        return self.options['rootDir'] is not None

    def _configure_device_manager(self, device_manager):
        """
        Configures the DeviceManager instance with the selected options.

        Args:
            device_manager (DeviceManager): The DeviceManager instance to configure.
        """
        # Set the device-specific configurations
        device_manager.numTypes = self.num_types
        device_manager.typeNames = self.type_names
        device_manager.typeColors = self.type_colors
        device_manager.rootDir = self.options.get('rootDir')
        device_manager.verbose = self.options.get('verbose')

        # Set the operational options (excluding numTypes, typeNames, typeColors, and rootDir)
        device_manager.options = {
            k: v for k, v in self.options.items() if k not in ['numTypes', 'typeNames', 'typeColors', 'rootDir', 'verbose']
        }

        # Apply the options to the device manager
        device_manager._apply_gui_options()


class ImageTypeChangerGui:
    """
    A GUI class for confirming or changing image types within a device.

    Attributes:
        device (Device): The device containing images to confirm or change types for.
    """

    def __init__(self, device):
        """Initializes the ImageTypeChangerGui with a device."""
        self.device = device

    def confirm_and_change_image_type(self):
        """
        Iterates through all images in the device and allows the user to confirm or change their types.
        """
        for img_type, image_paths in self.device.get_image_paths().items():
            if not image_paths:
                continue

            image_paths = self._ensure_list(image_paths)
            valid_types = self.device.get_typeNames()

            for image_path in image_paths:
                new_type = self._show_image_and_get_new_type(image_path, img_type, valid_types)
                if new_type and new_type != img_type:
                    self._update_image_type(image_path, img_type, new_type)

    def _show_image_and_get_new_type(self, image_path, current_type, valid_types):
        """
        Displays the image and prompts the user to confirm or change its type.

        Args:
            image_path (str): The file path of the image to display.
            current_type (str): The current image type.
            valid_types (list): A list of valid image types to choose from.

        Returns:
            str: The new image type selected by the user, or None if canceled.
        """
        image = IJ.openImage(image_path)
        image.show()

        new_type = self._get_user_input(current_type, valid_types)

        image.close()
        return new_type

    def _get_user_input(self, current_type, valid_types):
        """
        Sets up the GUI dialog to get user input for changing image type.

        Args:
            current_type (str): The current image type.
            valid_types (list): A list of valid image types to choose from.

        Returns:
            str: The new image type selected by the user, or None if canceled.
        """
        dialog = gui.GenericDialog("Confirm or Change Image Type")
        dialog.addMessage("Current Type: {}".format(current_type))
        dialog.addRadioButtonGroup("Select new type:", valid_types, 1, len(valid_types), current_type)
        dialog.setOKLabel("Next...")
        dialog.setCancelLabel("Cancel")
        dialog.showDialog()

        if dialog.wasCanceled():
            return None

        return dialog.getNextRadioButton()

    def _update_image_type(self, image_path, old_type, new_type):
        """
        Updates the image type and logs the change if verbose mode is enabled.

        Args:
            image_path (str): The file path of the image to update.
            old_type (str): The old image type.
            new_type (str): The new image type.
        """
        image = self.device._load_image(image_path)
        self.device.update_image_type(image_path, old_type, new_type, image)

        if self.device.verbose:
            print("Image type changed: {} from {} to {}".format(image_path, old_type, new_type))

    def _ensure_list(self, item):
        """
        Ensures that the provided item is returned as a list.

        Args:
            item: The item to ensure as a list.

        Returns:
            list: The item as a list, or a list containing the item if it was not already a list.
        """
        return item if isinstance(item, list) else [item]
