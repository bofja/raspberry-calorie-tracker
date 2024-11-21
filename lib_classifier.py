# Used when classifying food types
# Input is food images, tensor models, and tensor labels

import numpy
from PIL import Image
import tflite_runtime.interpreter as tflite

class Classifier:
   def __init__(self, model, label, mean = 127.5, std = 127.5):
      # Mean and standard deviation for normalization
      self.mean = mean
      self.std = std
      # Load labels from a list or file
      self.label = self.__muat_label(label)
      # Initialize the interpreter model
      self.interpreter = tflite.Interpreter(model)
      self.interpreter.allocate_tensors()

   def __muat_label(self, label):
      # Check if the label type is an array
      if isinstance(label, (list, tuple, set)): pass
      else:
         try:
            # Try reading the labels as a file
            with open(label, "r") as file:
               # Save the lines of the label file names as a list
               label = [ lines.strip() for lines in file.readlines() ]
         except Exception:
            # Notify the user if the label cannot be defined
            print("Model label is neither a list nor a file...")
            return None
      # Remove duplicates in labels if any
      return list(dict.fromkeys(label))

   def classification(self, image):
      # Save the model details in and out
      tensor_entry = self.interpreter.get_input_details()
      tensor_out = self.interpreter.get_output_details()

      # Save the dimensions and resize the image
      width = tensor_entry[0]["shape"][1]
      height = tensor_entry[0]["shape"][2]
      image = Image.open(image).resize((width, height))

      # Widen the shape of the array to fit the image
      data_entry = numpy.expand_dims(image, axis = 0)
      if tensor_entry[0]["dtype"] == numpy.float32:
         # Normalize the input values
         input_data = (numpy.float32(input_data) - self.mean) / self.std

      # Predict the class of the current image
      self.interpreter.set_tensor(tensor_entry[0]["index"], input_data)
      self.interpreter.invoke()
      output_data = self.interpreter.get_tensor(tensor_entry[0]["index"])

      # Return the highest predicted class
      # TODO: Prevent output when the accuracy is poor
      output_max = numpy.squeeze(output_data).argmax()
      return self.label[output_max]
