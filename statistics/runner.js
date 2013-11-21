<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {'packages':['corechart','motionchart']});
      google.setOnLoadCallback(drawAll);

      var chart = null;
      var all_data = %(all_data)s;
      var viz_data = %(viz_data)s;
      var vizChart = null;
      
      function drawAll() {
        detectScreenSize();
        drawChart();
      }

      var winW = 630, winH = 460;
      function detectScreenSize() {
        if (document.body && document.body.offsetWidth) {
          winW = document.body.offsetWidth;
          winH = document.body.offsetHeight;
        }
        if (document.compatMode=='CSS1Compat' &&
            document.documentElement &&
            document.documentElement.offsetWidth ) {
          winW = document.documentElement.offsetWidth;
          winH = document.documentElement.offsetHeight;
        }
        if (window.innerWidth && window.innerHeight) {
          winW = window.innerWidth;
          winH = window.innerHeight;
        }
      }
      
      function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Model');
        data.addColumn('number', 'Event');
        data.addColumn('number', 'Temperature');
        data.addColumn('number', 'Energy');
        data.addColumn('number', 'Director Variance');
        data.addColumn('number', 'Average Director Distance from Original');
        data.addColumn('number', 'Number of Directors');
        data.addColumn('string', 'Potential');
        data.addColumn('string', 'Potential Approximation');
        data.addColumn('string', 'Process');
        data.addColumn('number', 'Time Used');

        for (var model in all_data) {
          for (var time_index in all_data[model]) {
            var r = all_data[model][time_index];
            data.addRow([model, parseInt(time_index), r.temperature, r.energy,
                         r.director_variance, r.avg_director_dist,
                         r.num_directors, r.potential, r.potential_approx,
                         r.process, r.time_used]);
          }
        }
        data.addRows[all_data];
        chart = new google.visualization.MotionChart(document.getElementById('chart_div'));
        chart.draw(data,
                   {width: parseInt(winW*0.5), height: parseInt(winH*0.5),
                    state: '{"xZoomedIn":false,"showTrails":true,"yZoomedDataMin":0,"yZoomedIn":false,"xAxisOption":"_ALPHABETICAL","orderedByX":false,"xLambda":1,"colorOption":"_UNIQUE_COLOR","nonSelectedAlpha":0.4,"playDuration":15000,"xZoomedDataMax":3,"sizeOption":"5","iconKeySettings":[],"duration":{"multiplier":1,"timeUnit":"Y"},"yZoomedDataMax":1,"orderedByY":false,"iconType":"BUBBLE","xZoomedDataMin":0,"dimensions":{"iconDimensions":["dim0"]},"time":"1900","uniColorForNonSelected":false,"yLambda":1,"yAxisOption":"2"}'});

        google.visualization.events.addListener(chart, 'statechange', function() {
          var state_string = chart.getState();
          if (state_string == null) {
            return;
          }

          selected_models = getSelectedModels(chart);
          if (selected_models.length == 0) {
            drawVisualDisplay("--", -1);
            return;
          }

          current_time = 0;
          time_matches = /"time":"([0-9]+)"/.exec(state_string);
          if (time_matches != null && time_matches.length > 1) {
            current_time = parseInt(time_matches[1]) - 1900;
          }

          //drawVisualDisplay(selected_models[0], current_time);
          drawVisualDisplay("--", -1);
          
/*          if (selected_models.length != 1) {
            drawVisualDisplay('--', []);
            return;
          }
          
          line_matches = /"iconType":"(LINE)"/.exec(state_string);
          if (line_matches != null && line_matches.length > 1) {
            drawVisualDisplay(0, selected_agent_ids);
            return;
          }

          time_matches = /"time":"([0-9]+)"/.exec(state_string);
          if (time_matches != null && time_matches.length > 1) {
            problem_id = parseInt(time_matches[1]) - 1900;
            drawEventChart(problem_id, selected_agent_ids);
          }*/
        });
      }

      function drawVisualDisplay(model, time) {
        var img = document.getElementById("viz_display_img");
        var title = document.getElementById("viz_display_title");

        if (model == "--" || time < 0) {
          img.width = 0;
          img.height = 0;
          img.src = "//:0";
          img.alt = "";
          title.innerHTML = "";
        } else {
          img.width = parseInt(winW*0.5);
          img.height = parseInt(winH*0.5);
          img.src = viz_data[model][time];
          img.alt = model + "[" + time + "]: " + viz_data[model][time].file;
          title.innerHTML = "'" + model + "' (time: " + time + ")";
        }
      }

      function getSelectedModels(chart) {
        var state_string = chart.getState();
        if (state_string == null) {
          return [];
        }

        var models = [];
        for (var model in all_data) {
          if (new RegExp('"' + model + '"').test(state_string)) {
            models.push(model);
          }
        }
        return models;
      }
/*
      function drawEventChart(problem_id, agent_ids) {
        var data = new google.visualization.DataTable();

        if (problem_id == '--' || agent_ids.length == 0) {
          data.addColumn('string', 'Nothing');
          data.addColumn('number', 0);
          new google.visualization.BarChart(document.getElementById('event_chart_div')).
            draw(data,
                {title: 'Problem: ' + problem_id.toString(),
                 width:1, height:1,
                 legend: {position: 'none'},
                 isStacked: true});
          return;
        }

        raw_data = buildProblemRawData(problem_id, agent_ids);

        data.addColumn('string', 'Agent');
        for (var i = 0; i  < raw_data.length; ++i) {
          data.addColumn('number', raw_data[i][0]);    
        }
  
        data.addRows(raw_data[0].length - 1);
        
        for (var i in agent_ids) {
          data.setValue(parseInt(i), 0, agent_ids[i]);
        }

        for (var j = 1; j < raw_data[0].length; ++j) {
          var last_time = 0.0;
          for (var i = 0; i  < raw_data.length; ++i) {
            current_time = parseFloat(raw_data[i][j][0]);
            if (current_time < 0) {
              break;
            }

            data.setValue(j-1, i+1, current_time - last_time);
            data.setFormattedValue(
                j-1, i+1, 'TIME: ' + raw_data[i][j][0].toString() + ': ' +
                          raw_data[i][j][1].toString());
            last_time = current_time;
          }
        }

        // Create and draw the visualization.
        var problem_title = 'Problem: ' + problem_id.toString();
        if (parseInt(problem_id) == 0) {
          problem_title = 'Average for all Problems';
        }
        new google.visualization.BarChart(document.getElementById('event_chart_div')).
            draw(data,
                {title: problem_title,
                 width: parseInt(winW*0.5), height: parseInt(winH*0.5),
                 vAxis:  {title: "Agent"},
                 hAxis:  {title: "Timeline"},
                 legend: {position: 'none'},
                 isStacked: true});
      }

      function buildProblemRawData(problem_id, agent_ids) { 
        // Construct the problem data list, which contains lists of events per
        // agent for the problem.
        highest_num_events = 0;
        problem_data = []
        for (var a in agent_ids) {
          agent_id = agent_ids[a];
          problems = all_data[agent_id];
          problem = problems[parseInt(problem_id)];

          keys = [];
          for (var time in problem.events) {
            keys.push(parseFloat(time));
          }
          keys.sort();
        
          agent_problem_data = [];
          for (var i in keys) {
            agent_problem_data.push([keys[i], problem.events[keys[i]]]);
          }
          problem_data.push(agent_problem_data);

          if (agent_problem_data.length > highest_num_events) {
            highest_num_events = agent_problem_data.length;
          }
        }

        // Construct the raw data itself.
        raw_data = []
        for (var i = 0; i < highest_num_events; ++i) {
          raw_data.push(['Step ' + (i+1).toString()]);
        }
        for (var i in problem_data) {
          agent_data = problem_data[i];
          for (var j in agent_data) {
            raw_data[j].push(agent_data[j]);
          }
          for (var j = agent_data.length; j < highest_num_events; ++j) {
            raw_data[j].push([-1, '']);
          }
        }

        return raw_data;
      }
*/
    </script>
  </head>
  <body>
    <table>
      <tr>
        <td>
          <div id="chart_div"/>
        </td>
        <td>
          <div id="viz_display_div">
            <span id="viz_display_title"/>
            <img name='viz_display_img' id="viz_display_img" src="//:0" width=0 height=0 alt=""/>
          </div>
        </td>
      </tr>
    </table>
  </body>
</html>
