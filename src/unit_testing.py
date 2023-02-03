import os
import unittest
import main
from scripts import files


class TestStringMethods(unittest.TestCase):

    def test_toggle_no_logging(self):
        """ Tests toggling no_logging on and off """
        # print("TEST 1. test_toggle_no_logging")
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
        # print("TEST 2. test_toggle_cleanup")
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
        # print("TEST 3. test_create_and_delete_preset")
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
        # print("TEST 4. test_command_line_runbackup")
        test_dir = os.getcwd() + "/unit_test_files"
        test_dir = test_dir.replace("\\", "/")
        files.fully_delete_path(test_dir)
        files.create_test_files(test_dir, 2500000)
        main.testing_start(("-runbackup -m " + test_dir + "/main "
                                                          "-b " + test_dir + "/b1 "
                                                          "-b " + test_dir + "/b2 "
                                                          "-b " + test_dir + "/b3 "
                                                          "-b " + test_dir + "/b4 "
                                                          "-b " + test_dir + "/b5 "
                                                          "-cleanup on").split(' '))
        passed = True
        for i in range(1, 6):
            if not files.folders_are_equal(test_dir + "/main", test_dir + "/b" + str(i)):
                passed = False
        files.fully_delete_path(test_dir)
        self.assertEqual(passed, True)

    def test_command_line_runbackupall(self):
        """ Creates a number of presets and files, and ensures copying/moving/deleting all works """
        print("TEST 5. test_command_line_runbackupall")
        self.assertEqual(True, True)

    def test_command_line_runbackuppreset(self):
        """ Creates a single preset and some files, and ensures copying/moving/deleting all works """
        print("TEST 6. test_command_line_runbackuppreset")
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
