import glob
import os

class StatisticsGenerator:
    """
    Generates all necessary statistics for displaying the motion chart of
    run results.
    """
    def __init__(self, runs_dir, image_dir, web_image_dir):
        self.runs_dir = runs_dir
        self.image_dir = image_dir
        self.web_image_dir = web_image_dir

    def generate(self, runs_patterns=None, only_complete=True,
                 generate_images=False):
        """
        Generates the statistics for all runs, or for a subset that matches
        specific text patterns, or only complete runs.
        Returns a dictionary by model of lists of tuples for each event in the
        run, and a dictionary by model of lists of image files to display the
        actual run.
        If generate_images is True, also uses AVIZ to create PNG files for the
        model itself, and links it in.
        """
        # Get all of the runs to generate statistics for.
        if not runs_patterns:
            runs_patterns = [""]
        runs = sum([self.getMatchingRuns(runs_pattern)
                    for runs_pattern in runs_patterns], [])
        runs.sort()

        # Go over all of the runs, and fill in the data per model.
        all_data = {}
        viz_data = {}
        for current_run in runs:
            states_dir = "%s/states" % current_run

            # If we only want complete runs, make sure the run completed.
            if only_complete:
                has_current = os.path.exists("%s/current.dat" % states_dir)
                has_final = os.path.exists("%s/final.dat" % states_dir)
                has_cooled = os.path.exists("%s/cooled.dat" % states_dir)
                is_complete = (has_current and has_final) or \
                              (has_cooled and has_final)
                if not is_complete:
                    print "Skipped '%s' because it is not complete." % (
                            current_run,)
                    continue

            # Extract the model name, and gather any model specific parameters.
            model = os.path.basename(current_run)
            model_file = glob.glob("%s/*.py" % current_run)
            if not model_file:
                print "Skipped '%s' because it had no model file." % (
                        current_run,)
                continue
            model_file = model_file[0]
            
            # Get the parameters from the model file.
            model = os.path.basename(model_file)[:-3]
            parameters = {}
            exec file(model_file, "r") in parameters

            # Gather model specific parameters.
            num_directors = reduce(lambda a,b: a*b,
                                   parameters["DIMENSIONS"],
                                   1)
            potential = str(parameters["TWO_SPIN_POTENTIAL"]).split(".")[-1]
            potential_approx = str(parameters["POTENTIAL"]).split(".")[-1]

            # Get the heating and cooling events.
            heating_events = self._getEvents(
                    current_run, parameters["MC_HEATER_AVIZ_OUTPUT_PATH"])
            cooling_events = self._getEvents(
                    current_run, parameters["MC_COOLER_AVIZ_OUTPUT_PATH"])

            # Create the images with AVIZ if necessary for both heating and
            # cooling processes.
            if generate_images:
                self._generateImages(model, current_run,
                                     parameters["MC_HEATER_AVIZ_OUTPUT_PATH"])
                self._generateImages(model, current_run,
                                     parameters["MC_COOLER_AVIZ_OUTPUT_PATH"])

            # Create the event list for this model.
            event_list = []
            image_list = []
            for (index, event) in enumerate(heating_events + cooling_events):
                process = "Cooling"
                if index < len(heating_events):
                    process = "Heating"

                event_list.append((
                    event[1], # Temperature
                    event[2], # Energy
                    event[3], # Director Variance
                    event[4], # Average Director Distance from Original
                    num_directors,
                    potential,
                    potential_approx,
                    process,
                    event[5], # Time Used
                ))

                image_list.append("%s/%s/%s.png" %
                                  (self.web_image_dir, model, event[0]))

            all_data[model] = event_list
            viz_data[model] = image_list

        return (all_data, viz_data)

    def getMatchingRuns(self, runs_pattern):
        """
        Returns all runs that match the given runs_pattern textually.
        runs_pattern may be a glob style formatted string.
        """
        return glob.glob("%s/*%s*" % (self.runs_dir, runs_pattern))

    def _getEvents(self, current_run, output_file_prefix):
        """
        Parses the output files for the given run, with the given prefix, and
        returns a list of tuples of the information within them.
        """
        # Get all of the output files, and the event info lines in the info
        # file that accompanies them.
        output_files = glob.glob("%s/%s*.xyz" % (current_run,
                                                 output_file_prefix))
        info_files = glob.glob("%s/%sinfo.txt" % (current_run,
                                                  output_file_prefix))
        if not output_files or not info_files:
            print "No '%s??????.xyz' output files for '%s'." % (
                    output_file_prefix, current_run)
            return []
        event_infos = file(info_files[0], "r").readlines()
        if len(event_infos) != len(output_files):
            print ("Number of events in '%sinfo.txt' is different than the " +
                   "number of output files for '%s'.") % (output_file_prefix,
                                                          current_run)
            return []

        # If the first field is surrounded by [] brackets, then it indicates
        # time and we should use that instead of the file timestamp.
        output_files.sort()
        start_time = os.path.getmtime(output_files[0])
        first_event_field = event_infos[0].strip().split("\t")[0]
        if first_event_field[0] == "[" and first_event_field[-1] == "]":
          start_time = float(first_event_field[1:-1])

        # Go over all of the events and fill in the information to return.
        events = []
        for i in range(1, len(event_infos)):
            # Get the event time.
            output_file = output_files[i]
            current_time = os.path.getmtime(output_file) - start_time

            # Get the event information from the info file.
            event_info = event_infos[i].strip()
            event_info_fields = event_info.split("\t")

            # If the first field is surrounded by [] brackets, then it indicates
            # time and we should use that instead of the file timestamp.
            first_event_field = event_info_fields[0]
            if first_event_field[0] == "[" and first_event_field[-1] == "]":
                current_time = float(first_event_field[1:-1])
                event_info_fields.pop(0)

            # Get all the fields.
            output_filename = os.path.basename(output_file)[:-4]
            temperature = float(event_info_fields[0])
            energy = float(event_info_fields[1])
            distance = 0.0
            if len(event_info_fields) >= 4:
                distance = (1.0 - float(event_info_fields[3])) / 2.0
            variance = 0.0
            if len(event_info_fields) >= 5:
                variance = float(event_info_fields[4])

            # Add to the events.
            events.append((
                output_filename,
                temperature,
                energy,
                variance,
                distance,
                current_time))

        return events

    def _generateImages(self, model, current_run, output_file_prefix):
        """
        Generates the PNG files using AVIZ for the given run directory and the
        given output file prefixes and the name of the model.
        """
        # Determine where the script is.
        generate_script_path = "./generate_model.sh"
        if not os.path.exists(generate_script_path):
            generate_script_path = "./statistics/generate_model.sh"
        if not os.path.exists(generate_script_path):
            print "Couldn't find model generation with AVIZ script."
            return

        # Set up the command line arguments.
        xyz_file_pattern = "%s/%s" % (current_run, output_file_prefix)
        output_directory = "%s/%s" % (self.image_dir, model)

        # Run the script.
        cmd_line = "%s %s %s %s" % (generate_script_path,
                                    xyz_file_pattern,
                                    output_directory,
                                    model)
        os.system(cmd_line)
