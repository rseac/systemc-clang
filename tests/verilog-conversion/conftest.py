"""Fixtures for testing"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(os.environ["SYSTEMC_CLANG"]) / "plugins" / "hdl"))
import glob
import pytest
import shutil
from util.conf import LLNLExampleTestingConfigurations
from util.conf import ExampleTestingConfigurations
from util.conf import TestingConfigurations
from util.conf import SanityTestingConfigurations
from util.conf import CustomTestingConfigurations
import driver as drv


# Handy paths
examples = Path(os.environ["SYSTEMC_CLANG"]) / "examples"
testdata = Path(os.environ["SYSTEMC_CLANG"]) / "tests" / "verilog-conversion" / "data"
zfpsynth = examples / "llnl-examples" / "zfpsynth"
zfpshared = zfpsynth / "shared"
zfpshared2 = zfpsynth / "shared2"
modules_examples = examples / "llnl-examples" / "modules"


# Helper functions
def load_file(path):
    with open(path, "r") as f:
        return f.read()


def load_module(mod_name):
    raise NotImplementedError

def get_iscs_tests():
    """retreive intel systemc compiler tests, these tests follow a certain pattern"""
    [
        "test_binary_iscs.cpp",
        "test_break_iscs.cpp",
        "test_child_module_iscs.cpp",
        "test_dowhile_iscs.cpp",
        "test_for_fcall_fail_iscs.cpp",
        "test_for_iscs.cpp",
        "test_forloop_other_types_iscs.cpp",
        "test_virtual1_iscs.cpp",
        "test_vname_iscs.cpp",
        "test_while_const_iscs.cpp",
        "test_while_iscs.cpp",
    ]


# NOTE: The usage of this list is specified in the README.md
# (name, design, extra_args, golden verilog, golden hcode)
test_data = [
    (
        "add",
        load_file(testdata / "add.cpp"),
        None,
        load_file(testdata / "add_hdl.txt.v"),
        load_file(testdata / "add_hdl.txt")
    ),
    # ('sreg',   load_file(), [], None),
    # ('member-variable-sc-buffer',   load_file(), [], None),
    # # shared
    # ('z1test', load_file(zfpsynth / 'zfp1/z1test.cpp'), ['-I', zfpshared.stem, '-I', zfpsynth / 'zfp1'], None),
    # ('z2test', load_file(zfpsynth / 'zfp2/z2test.cpp'), ['-I', zfpshared.stem, '-I', zfpsynth / 'zfp2'], None),
    # # shared2
    (
        "z3test",
        load_file(zfpsynth / "zfp3/z3test.cpp"),
        ("-I", zfpshared2.stem, "-I", zfpsynth / "zfp3"),
        None,
        None,
    ),
    # ('z4test', load_file(zfpsynth / 'zfp4/z4test.cpp'), ['-I', zfpshared2.stem, '-I', zfpsynth / 'zfp4', None]),
    # ('z5test', load_file(zfpsynth / 'zfp5/z5test.cpp'), ['-I', zfpshared2.stem, '-I', zfpsynth / 'zfp5', None])
    (
        "moving-average",
        load_file(modules_examples / "moving-average" / "moving-average.cpp"),
        ("-I", zfpshared2.stem, "-I", modules_examples / "moving-average"),
        None,
        None,
    ),
    (
       "test_while_iscs",
       load_file(testdata / "test_while_iscs.cpp"),
       None,
       None, # load_file(testdata / "test_while_iscs_hdl.txt.v"),
       None,
    ),
    # (
    #    "test_binary_iscs",
    #    load_file(testdata / "test_binary_iscs.cpp"),
    #    None,
    #    None, # load_file(testdata / "test_binary_iscs_hdl.txt.v"),
    # ),
    (
       "test_break_iscs",
       load_file(testdata / "test_break_iscs.cpp"),
       None,
       None, # load_file(testdata / "test_break_iscs_hdl.txt.v"),
       None,
    ),
    (
       "test_for_iscs",
       load_file(testdata / "test_for_iscs.cpp"),
       None,
       None, # load_file(testdata / "test_for_iscs_hdl.txt.v"),
       None,
    ),
    ( 
       "test_child_module_iscs",
       load_file(testdata / "test_child_module_iscs.cpp"),
       None,
       None,
       None,
    ),
    # ( 
    #     "test_dowhile_iscs",
    #     load_file(testdata / "test_dowhile_iscs.cpp"),
    #     None,
    #     None
    # ),
    # ( 
    #     "test_for_fcall_fail_iscs",
    #     load_file(testdata / "test_for_fcall_fail_iscs.cpp"),
    #     None,
    #     None,
    # ),
    # ( 
    #     "test_forloop_other_types_iscs",
    #     load_file(testdata / "test_forloop_other_types_iscs.cpp"),
    #     None,
    #     None
    # ),
    # ( 
    #     "test_virtual1_iscs",
    #     load_file(testdata / "test_virtual1_iscs.cpp"),
    #     None,
    #     None
    # ),
    # ( 
    #     "test_vname_iscs",
    #     load_file(testdata / "test_vname_iscs.cpp"),
    #     None,
    #     None
    # ),
    ( 
        "test_while_const_iscs",
        load_file(testdata / "test_while_const_iscs.cpp"),
        None,
        None,
        None,
    ),

]


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "verilog: cpp to verilog tests")
    pytest.sc_log = None  # open('log.csv', 'w')


@pytest.fixture
def llnldriver():
    """fixture for llnl example driver"""
    conf = LLNLExampleTestingConfigurations()
    llnl_driver = drv.SystemCClangDriver(conf)
    return llnl_driver


# @pytest.fixture(params=[13])
@pytest.fixture(params=list(range(1, 11)) + list(range(12, 16)))
def exdriver(request):
    """fixture for ex_* examples driver"""
    conf = ExampleTestingConfigurations(request.param)
    ex_driver = drv.SystemCClangDriver(conf)
    return ex_driver


@pytest.fixture
def sanitydriver():
    """fixture for sanity test driver"""
    conf = SanityTestingConfigurations()
    sanity_driver = drv.SystemCClangDriver(conf)
    return sanity_driver


@pytest.fixture
def testfolderdriver():
    """fixture for running tests in the test folder of
    the systemc-clang"""
    root_folder = os.environ["SYSTEMC_CLANG_BUILD_DIR"] + "../systemc-clang/tests/"
    conf = TestingConfigurations(
        root_folder=root_folder, golden_folder=[], header_folders=[]
    )
    testfolder_driver = drv.SystemCClangDriver(conf)
    return testfolder_driver


def get_custom_tests():
    """helper function for collecting custom tests"""
    root_folder = (
        os.environ["SYSTEMC_CLANG_BUILD_DIR"]
        + "/"
        + "tests/data/verilog-conversion-custom/"
    )
    folder_list = glob.glob(root_folder + "*")
    print(folder_list)
    for f in folder_list:
        assert os.path.isdir(f), "{} is not a directory".format(f)
    return list(map(lambda x: os.path.basename(x), folder_list))


# @pytest.fixture(params=get_custom_tests())
# def customdriver(request):
#     """fixture for custom test driver"""
#     conf = CustomTestingConfigurations(request.param)
#     custom_driver = drv.SystemCClangDriver(conf)
#     return custom_driver


@pytest.fixture()
def tool_output(pytestconfig):
    return pytestconfig.getoption("tool_output")


def pytest_addoption(parser):
    """add options for controlling the running of tests"""
    # whether output the clang output
    parser.addoption("--tool-output", action="store_true", default=False)


@pytest.fixture
def default_params():
    return [
        "-x",
        "c++",
        "-w",
        "-c",
        #"-std=c++17",
        "_-D__STDC_CONSTANT_MACROS",
        "-D__STDC_LIMIT_MACROS",
        "-DRVD",
    ]


@pytest.fixture
def simple_add_cpp():
    test_set = test_data[0]
    assert test_set[0] == "add"
    return test_set[1]


@pytest.fixture
def has_vivado():
    if shutil.which("vivado"):
        return True
    else:
        return False
