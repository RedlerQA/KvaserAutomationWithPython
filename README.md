# Kvaser CANlib Python Integration and Testing

This repository contains a Python wrapper and test suite for controlling motor drives using Kvaser CANlib via CANopen protocols. The project includes functions for handling various CANopen operations, such as setting motor profiles (velocity, position, current, torque) and interacting with the drive via SDO (Service Data Object) commands.

## Project Structure

- **KvaserLib.py**: This file contains Python functions for interacting with a motor drive over CAN using the Kvaser CANlib API. It includes functions for enabling/disabling the drive, setting operational modes, and executing motion commands in different profiles.

- **KvaserLibTests.py**: This test script leverages the functions defined in `KvaserLib.py` to test different motor control profiles. It includes tests for velocity, position, current, and torque modes.

## Requirements

To use this project, you'll need the following:

- Python 3.6+
- Kvaser CANlib (installed and configured)
- Kvaser Python canlib module (available via PyPI or Kvaser download page)
- A connected Kvaser CAN interface
- Motor drive compatible with CANopen protocol

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/kvaser-canlib-python.git
   cd kvaser-canlib-python
Install required Python packages: Install the canlib module from PyPI:

```bash
pip install canlib
Ensure Kvaser CANlib is installed: Download and install the Kvaser CANlib SDK and drivers from the Kvaser website.

### Usage
Running the Test Suite
Configure the Test Script:

Open KvaserLibTests.py and adjust the NODE_ID, TIMEOUT_MS, and other parameters as needed for your specific setup.
Ensure the correct channel index is used in the open_channel() function.
Run the Test Script:

```bash
python KvaserLibTests.py
The test script will run a series of tests for different motor profiles (velocity, position, current, and torque). It will interact with the motor drive, sending commands and reading responses to verify proper operation.

### Customizing the Library
You can customize the functions in KvaserLib.py for your specific motor drive and CANopen implementation. Refer to the drive's documentation for specific SDO indexes, subindexes, and expected data formats.

### Contributing
Contributions are welcome! If you have suggestions for improvements or new features, feel free to submit a pull request or open an issue on GitHub.

### Acknowledgments
Kvaser CANlib for providing the CANlib SDK and documentation.
Python community for providing an open-source platform to build upon.

### **Instructions for Use**
- **Clone the Repository**: Begin by cloning the repository to your local machine.
- **Install Dependencies**: Install the necessary Python modules and Kvaser CANlib SDK.
- **Running the Tests**: Follow the instructions to run the test script, adjusting the configuration as needed.

This `README.md` file is designed to be informative and user-friendly, guiding users through setting up 
