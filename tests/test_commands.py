from unittest import TestCase
import os

# set environ vars so when cfg.py is called, it gets
# test enviroment vars
oldBotNick = os.environ.get("BOTNICK", "")
oldBotChat = os.environ.get("BOTCHAT", "")
oldBotAuth = os.environ.get("BOTAUTH", "")
os.environ["BOTNICK"] = "bot"
os.environ["BOTCHAT"] = "bot"
os.environ["BOTAUTH"] = "oauth:bot"


import commands
from commands import roll


# Reset the old enviroment vars
os.environ["BOTNICK"] = oldBotNick
os.environ["BOTCHAT"] = oldBotChat
os.environ["BOTAUTH"] = oldBotAuth


class TestSock(object):
    """
    _chat gets called and then calls the `send` method of the passed sock. Here
    we are returning the message so that the test can be on the returned string
    not send the message to the irc server.
    """
    def send(self, msg):
        return str(msg)


testSock = TestSock()


class TestCommand(TestCase):
    command = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cmdError = commands.RESPONSES[self.command]["error"]
        cmdSuccess = commands.RESPONSES[self.command]["success"]
        self.error = {key : "/me : {}".format(value) for key, value in cmdError.items()}
        self.success = {key : "/me : {}".format(value) for key, value in cmdSuccess.items()}

    def cmdResponse(self, addArgs):
        addArgs = addArgs if isinstance(addArgs, list) else [addArgs]
        self.args += addArgs
        cmd = getattr(commands, self.command)
        return cmd(self.args)

    def shouldEqual(self, addArgs, expect):
        response = self.cmdResponse(addArgs)
        self.assertEqual(response,
                         expect)

    def shouldNotEqual(self, addArgs, expect):
        response = self.cmdResponse(addArgs)
        self.assertNotEqual(response,
                            expect)

    def shouldNotFail(self, addArgs):
        response = self.cmdResponse(addArgs)
        for err in self.error.values():
            self.assertNotEqual(response,
                                err)


    def setUp(self):
        self.args = [testSock, "test_user"]

    def tearDown(self):
        del self.args


class TestRoll(TestCommand):
    command = "roll"

    # edge cases
    def test_no_arg(self):
        self.shouldEqual("", self.error['bad_args'])

    def test_zero(self):
        self.shouldEqual("0", self.error['bad_args'])
        self.shouldEqual("0d", self.error['bad_args'])
        self.shouldEqual("d0", self.error['bad_args'])
        self.shouldEqual("0d8", self.error['bad_args'])
        self.shouldEqual("3d0", self.error['bad_args'])

    def test_neg_num(self):
        self.shouldEqual("-3", self.error['bad_args'])
        self.shouldEqual("-3d", self.error['bad_args'])
        self.shouldEqual("-3d-8", self.error['bad_args'])
        self.shouldEqual("3d-8", self.error['bad_args'])
        self.shouldEqual("d-8", self.error['bad_args'])

    # too large of rolls
    def test_too_many_dice(self):
        self.shouldEqual("{}d10".format(commands.MAX_DICE + 1), self.error['too_many_dice'])

    def test_equal_too_many_dice(self):
        self.shouldEqual("{}d10".format(commands.MAX_DICE), self.error['too_many_dice'])

    def test_too_many_dsides(self):
        self.shouldEqual("10d{}".format(commands.MAX_DSIDES + 1), self.error['too_many_dsides'])

    def test_equal_too_many_dsides(self):
        self.shouldEqual("10d{}".format(commands.MAX_DSIDES), self.error['too_many_dsides'])


    def test_plural(self):
        response = self.cmdResponse("2d10")
        assert 'dice' in response
        assert 'add' in response

    def test_singular(self):
        response = self.cmdResponse("d10")
        assert 'die' in response

    # num
    def test_roll_num(self):
        self.shouldNotFail("3")

    def test_roll_num_d(self):
        self.shouldEqual("3d", self.error['bad_args'])
        self.shouldEqual("3D", self.error['bad_args'])

    def test_roll_num_d_num(self):
        self.shouldNotFail("3d8")
        self.shouldNotFail("3D8")

    def test_roll_num_d_char(self):
        self.shouldEqual("3da", self.error['bad_args'])
        self.shouldEqual("3Da", self.error['bad_args'])

    # d
    def test_roll_d(self):
        self.shouldEqual("d", self.error['bad_args'])
        self.shouldEqual("D", self.error['bad_args'])

    def test_roll_d_num(self):
        self.shouldNotFail("d8")
        self.shouldNotFail("D8")

    def test_roll_d_char(self):
        self.shouldEqual("da", self.error['bad_args'])
        self.shouldEqual("Da", self.error['bad_args'])

    # char
    def test_roll_char(self):
        self.shouldEqual("c", self.error['bad_args'])
        self.shouldEqual("C", self.error['bad_args'])

    def test_roll_chars(self):
        self.shouldEqual("copper", self.error['bad_args'])
        self.shouldEqual("Can", self.error['bad_args'])

    def test_roll_char_d(self):
        self.shouldEqual("cd", self.error['bad_args'])
        self.shouldEqual("cD", self.error['bad_args'])

    def test_roll_char_d_num(self):
        self.shouldEqual("cd8", self.error['bad_args'])
        self.shouldEqual("cD8", self.error['bad_args'])

    def test_roll_char_d_char(self):
        self.shouldEqual("cda", self.error['bad_args'])
        self.shouldEqual("cDa", self.error['bad_args'])
