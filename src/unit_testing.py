import os
import unittest
from os.path import exists

import main
from scripts import files
from scripts import logging


class TestStringMethods(unittest.TestCase):

    def test_command_line_logfilemax(self):
        """ Creates a single preset and some files, and ensures copying/moving/deleting all works """
        print(">>>>>>>TEST test_command_line_logfilemax")
        test_value_string = "57"
        test_value_int = 57
        # 1. Running command, including nologging off since logging is needed
        main.testing_start(("-logfilemax " + test_value_string + " -nologging off").split(' '))
        # 2. Config file check
        if files.get_line_from_cfg("log_file_max") != test_value_string:
            print("test_command_line_logfilemax FAILED, config file not properly changed")
            self.assertEqual(files.get_line_from_cfg("log_file_max"), test_value_string)
            return
        # 3. Testing printing log and ensuring it caps out at the correct point
        main.program.saving.load_settings_from_config()
        new_log_files = []
        count = 0
        while len(os.listdir(os.getcwd() + "/log")) < test_value_int:
            count += 1
            filename, trashed_file = logging.print_log("Test Log" + str(count))
            new_log_files.append(os.getcwd() + "/log/" + filename)
        for i in range(5):
            count += 1
            filename, trashed_file = logging.print_log("Test Log" + str(count))
            new_log_files.append(os.getcwd() + "/log/" + filename)
        count += 1
        filename, trashed_a_log_file = logging.print_log("Test Log" + str(count))
        new_log_files.append(os.getcwd() + "/log/" + filename)
        if not trashed_a_log_file:
            print("test_command_line_logfilemax FAILED, log file overflow trashing not working")
            self.assertEqual(False, True)
            return
        # 4. clearing test log files
        for file in new_log_files:
            if exists(file):
                os.remove(file)


        passed = True
        # first the test should test that the config file actually is having the value added to it
        # this test should actually fill the log to the max, test where it cuts off, and then delete all the newly
        # created files, while leaving any older log files that existed before.


        self.assertEqual(True, True)

    def test_command_line_no_logging(self):
        """ Tests toggling no_logging on and off """
        print(">>>>>>>TEST test_command_line_no_logging")
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

    def test_command_line_cleanup(self):
        """ Tests toggling cleanup on and off """
        print("TEST test_command_line_cleanup")
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

    def test_command_line_create_and_delete_preset(self):
        """ Creates a number of presets and files, and ensures copying/moving/deleting all works """
        print(">>>>>>>TEST test_create_and_delete_preset")
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
        print(">>>>>>>TEST test_command_line_runbackup")

        # print("SKIPPING FOR NOW TO SAVE TIME, REMOVE THIS")
        # self.assertEqual(True, True)
        # return

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
                                                          "-cleanup on -nologging off").split(' '))
        passed = True
        for i in range(1, 6):
            if not files.folders_are_equal(test_dir + "/main", test_dir + "/b" + str(i)):
                passed = False
                break
        files.fully_delete_path(test_dir)
        self.assertEqual(passed, True)

    def test_command_line_runbackupall(self):
        """ Creates a number of presets and files, and ensures copying/moving/deleting all works """
        print(">>>>>>>TEST test_command_line_runbackupall")

        # print("SKIPPING FOR NOW TO SAVE TIME, REMOVE THIS")
        # self.assertEqual(True, True)
        # return

        preset_names = ["Test Preset 11", "Test Preset 22", "Test Preset 33"]
        test_dirs = [(os.getcwd() + "/unit_test_files1").replace("\\", "/"),
                     (os.getcwd() + "/unit_test_files2").replace("\\", "/"),
                     (os.getcwd() + "/unit_test_files3").replace("\\", "/")]
        for i in range(len(preset_names)):
            files.fully_delete_path(test_dirs[i])
            files.create_test_files(test_dirs[i], 1000000)
            # create preset
            main.testing_start(("-createpreset " + preset_names[i] +
                                " -m " + test_dirs[i] + "/main "
                                 "-b " + test_dirs[i] + "/b1 "
                                 "-b " + test_dirs[i] + "/b2 "
                                 "-b " + test_dirs[i] + "/b3 "
                                 "-b " + test_dirs[i] + "/b4 "
                                 "-b " + test_dirs[i] + "/b5 "
                                 "-cleanup on -nologging off").split(' '))
            if not files.exists_in_cfg("preset=" + preset_names[i], "/presets/presets.cfg"):
                self.assertEqual("FAILED for -createpreset command", False)
                return

        # run preset
        main.testing_start(["-runbackupall", ""])

        # delete preset
        for i in range(len(preset_names)):
            main.testing_start(("-deletepreset " + preset_names[i]).split(' '))
            if files.exists_in_cfg(preset_names[i], "/presets/presets.cfg"):
                self.assertEqual("FAILED for -deletepreset command", False)
                return

        passed = True
        for i in range(len(preset_names)):
            for j in range(1, 6):
                if not files.folders_are_equal(test_dirs[i] + "/main", test_dirs[i] + "/b" + str(j)):
                    passed = False
                    break
            files.fully_delete_path(test_dirs[i])
        if not passed:
            self.assertEqual("FAILED for -runpreset command", False)
            return
        self.assertEqual(passed, True)

    def test_command_line_runbackuppreset(self):
        """ Creates a single preset and some files, and ensures copying/moving/deleting all works """
        print(">>>>>>>TEST test_command_line_runbackuppreset")

        # print("SKIPPING FOR NOW TO SAVE TIME, REMOVE THIS")
        # self.assertEqual(True, True)
        # return

        preset_name = "Test Preset 11"
        test_dir = os.getcwd() + "/unit_test_files"
        test_dir = test_dir.replace("\\", "/")
        files.fully_delete_path(test_dir)
        files.create_test_files(test_dir, 2500000)
        # create preset
        main.testing_start(("-createpreset " + preset_name + " -m " + test_dir + "/main "
                                                             "-b " + test_dir + "/b1 "
                                                             "-b " + test_dir + "/b2 "
                                                             "-b " + test_dir + "/b3 "
                                                             "-b " + test_dir + "/b4 "
                                                             "-b " + test_dir + "/b5 "
                                                             "-cleanup on -nologging off").split(' '))
        if not files.exists_in_cfg("preset=" + preset_name, "/presets/presets.cfg"):
            self.assertEqual("FAILED for -createpreset command", False)
            return
        # run preset
        main.testing_start(("-runpreset " + preset_name).split(' '))

        # delete preset
        main.testing_start(("-deletepreset " + preset_name).split(' '))
        if files.exists_in_cfg(preset_name, "/presets/presets.cfg"):
            self.assertEqual("FAILED for -deletepreset command", False)
            return

        passed = True
        for i in range(1, 6):
            if not files.folders_are_equal(test_dir + "/main", test_dir + "/b" + str(i)):
                passed = False
                break
        files.fully_delete_path(test_dir)
        if not passed:
            self.assertEqual("FAILED for -runpreset command", False)
            return
        self.assertEqual(passed, True)

    def test_command_line_move_preset(self):
        """ """
        print(">>>>>>>TEST test_command_line_move_preset")

        self.assertEqual(True, True)

    def test_command_line_skip_file(self):
        """  """
        print(">>>>>>>TEST test_command_line_move_preset")

        self.assertEqual(True, True)

    def test_command_line_skip_folder(self):
        """  """
        print(">>>>>>>TEST test_command_line_move_preset")

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
