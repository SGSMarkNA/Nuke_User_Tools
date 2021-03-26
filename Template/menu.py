from ..menu_maker import Add_Command

from   example_01 import Example_01_Command
import example_02
import package_example

Add_Command(Example_01_Command)
Add_Command(example_02.Example_02_Command)
Add_Command(package_example.package_Module.Package_Example_Command)

