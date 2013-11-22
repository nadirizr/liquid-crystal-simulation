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

def writeResultsToCsvFile(filename, results):
  col_names = ["Agent", "Problem", "Time Limit", "Used Time", "Time Consumption",
               "Average Time Consumption", "Solution Length", "Optimal Solution Length",
               "Score", "Average Score", "Failure Rate", "Expanded Nodes"]
  table_str = ",".join(["'" + str(col) + "'" for col in col_names]) + "\n"
  for agent_name in results:
    for i, p in enumerate(results[agent_name]):
      problem_name = str(i)
      if i == 0:
        problem_name = "Average"
      solution_length = p[5] and len(p[5]) or None
      score = p[5] and (float(p[0][2]) / float(solution_length)) or 0.0
      table_row = [agent_name, problem_name, p[1], p[2], p[3], p[4], solution_length,
                   p[0][2], score, p[6], p[7], p[8]]
      table_str += ",".join(["'" + str(val) + "'" for val in table_row]) + "\n"

  f = open(filename, "w")
  f.write(table_str)
  f.flush()
  f.close()

# Treat all arguments as runs patterns.
runs_patterns = sys.argv[1:]
if not runs_patterns:
    runs_patterns = [""]

generator = StatisticsGenerator("runs")

print "#"*80
print "Generating statistics for runs:"
print "\n".join(["\n".join(generator.getMatchingRuns(runs_pattern))
                 for runs_pattern in runs_patterns])
print "#"*80
print

all_data, viz_data = generator.generate(runs_patterns)
writeResultsToHtmlFile("compare_chart.html", all_data, viz_data)
#writeResultsToCsvFile("compare_chart.csv", results)
