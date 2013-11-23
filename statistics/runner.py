import sys
import re

from statistics.generator import *

def writeResultsToHtmlFile(filename, all_data, viz_data):
    js_code = ""
    try:
        js_code = open("statistics/runner.js","r").read()
    except:
        try:
            js_code = open("runner.js","r").read()
        except:
            return

    num_models_out = len(all_data)
    all_data_out = "{\n"
    viz_data_out = "{\n"
    for (model, event_infos) in all_data.items():
        viz_data_images = viz_data[model]

        all_data_out += (
"""          '%s': {
""" % model)
        viz_data_out += (
"""          '%s': {
""" % model)

        for event_index, event_info in enumerate(event_infos):
            all_data_out += (
"""            %d: { 'time': %s,
                     'temperature': %s,
                     'energy': %s,
                     'director_variance': %s,
                     'avg_director_dist': %s,
                     'num_directors': %s,
                     'potential': '%s',
                     'potential_approx': '%s',
                     'process': '%s',
                     'time_used': %d },
""" % ((event_index, event_index) + event_info))
            viz_data_out += (
"""            %d: { 'file': '%s' },
""" % (event_index, viz_data_images[event_index]))

        all_data_out += (
"""          },
""")
        viz_data_out += (
"""          },
""")

    all_data_out += (
"""        };
""")
    viz_data_out += (
"""        };
""")

    f = open(filename, "w");
    f.write(js_code % {
        "num_models": str(num_models_out),
        "all_data": str(all_data_out),
        "viz_data": str(viz_data_out),
    })
    f.flush()
    f.close()

args = sys.argv[1:]

# Check if the user selected -a or --aviz.
generate_images_with_aviz = False
if "-a" in args:
    generate_images_with_aviz = True
    args.remove("-a")
if "--aviz" in args:
    generate_images_with_aviz = True
    args.remove("--aviz")

# Treat all other arguments as runs patterns.
runs_patterns = args[:]
if not runs_patterns:
    runs_patterns = [""]

generator = StatisticsGenerator("runs", "web/models", "models")

print "#"*80
print "Generating statistics for runs:"
print "\n".join(["\n".join(generator.getMatchingRuns(runs_pattern))
                 for runs_pattern in runs_patterns])
print "#"*80
print

all_data, viz_data = generator.generate(
        runs_patterns,
        only_complete=True,
        generate_images=generate_images_with_aviz)
writeResultsToHtmlFile("web/compare_chart.html", all_data, viz_data)
