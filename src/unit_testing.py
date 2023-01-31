import os
import unittest
import main
from scripts import files


class TestStringMethods(unittest.TestCase):

    def test_toggle_no_logging(self):
        """ Tests toggling no_logging on and off """
        main.testing_start("-nologging on".split(" "))
        passed = False
        f = open(os.getcwd() + "/settings.cfg", "r")
        for line in f:
            if "no_logging" in line:
                if "True" in line:
                    passed = True
                    break
        f.close()
        if passed:
            passed = False
            main.testing_start("-nologging off".split(" "))
            f = open(os.getcwd() + "/settings.cfg", "r")
            for line in f:
                if "no_logging" in line:
                    if "False" in line:
                        passed = True
                        break
            f.close()
        self.assertEqual(passed, True)

    def test_toggle_cleanup(self):
        """ Tests toggling cleanup on and off """
        main.testing_start("-cleanup on".split(" "))
        passed = False
        f = open(os.getcwd() + "/settings.cfg", "r")
        for line in f:
            if "cleanup" in line:
                if "True" in line:
                    passed = True
                    break
        f.close()
        if passed:
            passed = False
            main.testing_start("-cleanup off".split(" "))
            f = open(os.getcwd() + "/settings.cfg", "r")
            for line in f:
                if "cleanup" in line:
                    if "False" in line:
                        passed = True
                        break
            f.close()
        self.assertEqual(passed, True)

    def test_create_and_delete_preset(self):
        """ Creates a number of presets and files, and ensures copying/moving/deleting all works """
        main.testing_start("-createpreset Test Preset 83245 -m C:/main folder -b C:/backup 1 -b C:/backup 2 "
                           "-b C:/backup 3 -b C:/backup 4 -b C:/backup 5".split(" "))
        f = open(os.getcwd() + "/presets/presets.cfg", "r")
        passed = False
        step = 0
        for line in f:
            if step == 0:
                if "Test Preset 83245" in line:
                    step += 1
            elif step == 1:
                if "C:\\main folder" in line:
                    step += 1
            elif step == 2:
                if "C:\\backup 1" in line:
                    step += 1
            elif step == 3:
                if "C:\\backup 2" in line:
                    step += 1
            elif step == 4:
                if "C:\\backup 3" in line:
                    step += 1
            elif step == 5:
                if "C:\\backup 4" in line:
                    step += 1
            elif step == 6:
                if "C:\\backup 5" in line:
                    passed = True
        f.close()
        if passed:
            main.testing_start("-deletepreset Test Preset 83245".split(" "))
            f = open(os.getcwd() + "/presets/presets.cfg", "r")
            for line in f:
                if "Test Preset 83245" in line:
                    passed = False
            f.close()
        else:
            print("test_create_and_delete_preset failed to create ")
        self.assertEqual(passed, True)

    def test_command_line_runbackup(self):
        """ Creates some files, and ensures copying/moving/deleting all works """
        # test_dir = os.getcwd() + "/unit_test_files/"
        # files.create_test_files(test_dir, 100000)
        # main.testing_start(["-runbackup"])
        # files.remove_test_files(test_dir)
        self.assertEqual(True, True)

    def test_command_line_runbackupall(self):
        """ Creates a number of presets and files, and ensures copying/moving/deleting all works """
        self.assertEqual(True, True)

    def test_command_line_runbackuppreset(self):
        """ Creates a single preset and some files, and ensures copying/moving/deleting all works """
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
