from unittest import TestCase
import commands
from commands import roll

def fake_sock():
    pass


class TestCommand(TestCase):
    command = ""
    badResponse = ""

    def cmdResponse(self, addArgs):
        addArgs = addArgs if isinstance(addArgs, list) else [addArgs]
        self.args += addArgs
        cmd = getattr(commands, self.command)
        return cmd(self.args)


    def shouldPass(self, addArgs, expect=None):
        expect = expect if expect else self.badResponse
        response = self.cmdResponse(addArgs)
        self.assertNotEqual(response,
                            expect)

    def shouldFail(self, addArgs, expect=None):
        expect = expect if expect else self.badResponse
        response = self.cmdResponse(addArgs)
        self.assertEqual(response,
                         expect)

    def setUp(self):
        self.args = [fake_sock, "test_user"]

    def tearDown(self):
        del self.args


class TestRoll(TestCommand):
    command = "roll"
    badResponse = commands.BAD_ARG_RESPONSE["roll"]

    # edge cases
    def test_no_arg(self):
        self.shouldFail("")

    def test_zero(self):
        self.shouldFail("0")
        self.shouldFail("0d")
        self.shouldFail("d0")
        self.shouldFail("0d8")
        self.shouldFail("3d0")

    def test_neg_num(self):
        self.shouldFail("-3")
        self.shouldFail("-3d")
        self.shouldFail("-3d-8")
        self.shouldFail("3d-8")
        self.shouldFail("d-8")

    # num
    def test_roll_num(self):
        self.shouldPass("3")

    def test_roll_num_d(self):
        self.shouldFail("3d")
        self.shouldFail("3D")

    def test_roll_num_d_num(self):
        self.shouldPass("3d8")
        self.shouldPass("3D8")

    def test_roll_num_d_char(self):
        self.shouldFail("3da")
        self.shouldFail("3Da")

    # d
    def test_roll_d(self):
        self.shouldFail("d")
        self.shouldFail("D")

    def test_roll_d_num(self):
        self.shouldPass("d8")
        self.shouldPass("D8")

    def test_roll_d_char(self):
        self.shouldFail("da")
        self.shouldFail("Da")

    # char
    def test_roll_char(self):
        self.shouldFail("c")
        self.shouldFail("C")

    def test_roll_chars(self):
        self.shouldFail("copper")
        self.shouldFail("Can")

    def test_roll_char_d(self):
        self.shouldFail("cd")
        self.shouldFail("cD")

    def test_roll_char_d_num(self):
        self.shouldFail("cd8")
        self.shouldFail("cD8")

    def test_roll_char_d_char(self):
        self.shouldFail("cda")
        self.shouldFail("cDa")
