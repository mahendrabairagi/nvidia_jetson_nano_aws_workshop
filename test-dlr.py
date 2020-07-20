from dlr import DLRModel
import numpy as np
import os
import logging
import sys

def test_model(data):
        # Load the model
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'test_model')
    device = 'gpu'
    model = DLRModel(model_path, device)

    # Run the model
    image = np.load(os.path.join(data)).astype(np.float32)
    #flatten within a input array
    input_data = {'data': image}
    probabilities = model.run(input_data) #need to be a list of input arrays matching input names
    print probabilities[0]
    print probabilities[0].argmax()


if __name__ == '__main__':
    data = sys.argv[1]
    logging.basicConfig(filename='test-dlr.log',level=logging.INFO)
    test_model(data)
#    test_multi_input()
#    test_multi_input_multi_output()
    logging.info('All tests passed!')
