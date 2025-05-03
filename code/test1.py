import functions.rawplotter as plotter
import functions.instruction_segregator as segregator

function = 2

if function == 1:
    plotter.plot_files("data/raw/", ["granade.csv"], rows=range(3))

elif function == 2:
    plotter.plot_folder("data/punch/", rows=range(3), sub_plot=True, columns=(5, 85), interval=(0, 17))

elif function == 3:
    segregator.plotter("data/raw/granade.csv", std_threshold = 150)

elif function == 4:
    segregator.csv_file("data/raw/granade.csv", csv_location = "features/granade")