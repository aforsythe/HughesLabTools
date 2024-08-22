from ij import IJ, Prefs
import os
from os.path import join, splitext
from HughesLabTools.DeviceImage import DeviceImage

class VesselImage(DeviceImage):
    def __init__(self, title=None, img=None):
        if title is not None and img is not None:
            super(VesselImage, self).__init__(title, img)
        elif title is not None:
            super(VesselImage, self).__init__(title)
        else:
            super(VesselImage, self).__init__()

    def threshold_and_mask(self, device_manager):
        """
        Apply thresholding and convert the image to a mask. Save the result and optionally show it.

        Args:
            device_manager (DeviceManager): The DeviceManager instance containing options like 'show_threshold'.
        """
        # Duplicate the image
        imp2 = self.duplicate()

        # Set the title of the duplicated image
        imp2.setTitle(splitext(self.getTitle())[0] + '_threshold')

        # Apply threshold and convert to mask
        IJ.setAutoThreshold(imp2, 'Li dark b&w')
        Prefs.blackBackground = True
        IJ.run(imp2, 'Convert to Mask', '')

        # Save the thresholded image
        output_dir = join(self.getOriginalFileInfo().directory, 'thresholded')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = join(output_dir, splitext(self.getTitle())[0] + '_thresholded.jpg')
        self.save(output_path)

        # Verbose logging
        if device_manager.verbose:
            device_manager.log(f"Thresholded image saved at: {output_path}")

        # Optionally show the thresholded image
        if device_manager.options.get('show_threshold', False):
            imp2.show()

        return imp2

