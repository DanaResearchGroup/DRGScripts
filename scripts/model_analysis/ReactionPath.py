
# Viewing a reaction path diagram in Cantera.

# This script uses Graphviz to generate an image. You must have Graphviz installed
# and the program 'dot' must be on your path for this example to work.
# Graphviz can be obtained from https://www.graphviz.org/ or (possibly) installed
# using your operating system's package manager.

# Requires: cantera >= 2.5.0

# run in t3_env


from subprocess import run
import sys
from pathlib import Path
import cantera as ct


time = 2*(10**(-3))  # set how long the path diagram should run in seconds

# set the cantera file path and initial parameters (Temp, Preasure, X)
cti_path = '/home/navedanan/Code/runs/alonx1002/test/chem_annotated.cti'
gas = ct.Solution(cti_path)
gas.TPX = 997.0, ct.one_atm, 'C12H26(1):0.02, Ar:0.98'
r = ct.IdealGasReactor(gas, energy='off')  # energy is set to 'off' if you want isothermal reaction other wise set to 'on'
net = ct.ReactorNet([r])

T = r.T  # get the tempratures from the IdealGasReactor
counter = 10**5  # set max iterations so it wont be infinte loop (100,000)
loop = 0  # used to follow the while loop for debug (not mendatory)

# consider changing the loop to iterate by time until time_max
while counter >= 0:
    loop +=1
    # print(f'loop num {loop}')
    net.advance(time)
    T = r.T
    counter -= 1
if counter < 0:
    print('Ooops something went worng')

element = 'H'  # follows only after elements in the periodic table

diagram = ct.ReactionPathDiagram(gas, element)
diagram.title = 'Reaction path in time spend of {0} milisecond \n At temprature of: {1} '.format(time*1000, "{:.2f}".format(T))
diagram.label_threshold = 0.5
diagram.bold_color = 'red'
# diagram.dashed_color = 'red'
print(diagram.normal_color)
print(diagram.dashed_color)
dot_file = '/home/navedanan/Code/runs/diagram.dot'
img_file = '/home/navedanan/Code/runs/diagram_pic.png'
img_path = Path.cwd().joinpath(img_file)
diagram.write_dot(dot_file)
# print(diagram.get_data())

print("Wrote graphviz input file to '{0}'.".format(Path.cwd().joinpath(dot_file)))

run('dot {0} -Tpng -o{1} -Gdpi=200'.format(dot_file, img_file).split())
print("Wrote graphviz output file to '{0}'.".format(img_path))
print(T)
if "-view" in sys.argv:
    import webbrowser
    webbrowser.open('file:///' + img_path)

