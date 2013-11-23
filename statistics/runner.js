<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load('visualization', '1', {'packages':['corechart','motionchart']});
      google.setOnLoadCallback(drawAll);

      var chart = null;
      var num_models = %(num_models)s;
      var all_data = %(all_data)s;
      var viz_data = %(viz_data)s;
      var vizChart = null;
      var data_field_names = ["time", "temperature", "energy",
                              "director_variance", "avg_director_dist",
                              "time_used", "num_directors", "potential",
                              "potential_approx", "process"];
      var data_field_titles = { 
          "time": "Time",
          "temperature": "Temperature",
          "energy": "Energy",
          "director_variance": "Director Variance",
          "avg_director_dist": "Average Director Distance from Original",
          "time_used": "Time Used",
          "num_directors": "Number of Directors",
          "potential": "Potential",
          "potential_approx": "Potential Approximation",
          "process": "Process",
      }
      
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
        data.addColumn('number', 'Time');
        data.addColumn('number', 'Temperature');
        data.addColumn('number', 'Energy');
        data.addColumn('number', 'Director Variance');
        data.addColumn('number', 'Average Director Distance from Original');
        data.addColumn('number', 'Time Used');
        data.addColumn('number', 'Number of Directors');
        data.addColumn('string', 'Potential');
        data.addColumn('string', 'Potential Approximation');
        data.addColumn('string', 'Process');

        for (var model in all_data) {
          for (var time_index in all_data[model]) {
            var r = all_data[model][time_index];
            data.addRow([model, parseInt(time_index), r.temperature, r.energy,
                         r.director_variance, r.avg_director_dist,
                         r.time_used, r.num_directors, r.potential,
                         r.potential_approx, r.process]);
          }
        }
        data.addRows[all_data];
        chart = new google.visualization.MotionChart(document.getElementById('chart_div'));
        chart.draw(data,
                   {width: parseInt(winW*0.5), height: parseInt(winH*0.5),
                    state: '{"xZoomedIn":false,"showTrails":true,"yZoomedDataMin":0,"yZoomedIn":false,"xAxisOption":"_TIME","orderedByX":false,"xLambda":1,"colorOption":"_UNIQUE_COLOR","nonSelectedAlpha":0.4,"playDuration":15000,"xZoomedDataMax":3,"sizeOption":"5","iconKeySettings":[],"duration":{"multiplier":1,"timeUnit":"Y"},"yZoomedDataMax":1,"orderedByY":false,"iconType":"BUBBLE","xZoomedDataMin":0,"dimensions":{"iconDimensions":["dim0"]},"time":"1900","uniColorForNonSelected":false,"yLambda":1,"yAxisOption":"2"}'});

        google.visualization.events.addListener(chart, 'statechange', function() {
          var state_string = chart.getState();
          if (state_string == null) {
            return;
          }

          // If there is a specific time selected, find it.
          current_time = 0;
          time_matches = /"time":"([0-9]+)"/.exec(state_string);
          if (time_matches != null && time_matches.length > 1) {
            current_time = parseInt(time_matches[1]) - 1900;
          }

          // Determine the X axis type.
          x_axis = 1;
          x_axis_matches = /"xAxisOption":"([0-9]+)"/.exec(state_string);
          if (x_axis_matches != null && x_axis_matches.length > 1) {
            x_axis = parseInt(x_axis_matches[1]);
          }
          x_axis_matches = /"xAxisOption":"(_TIME)"/.exec(state_string);
          if (x_axis_matches != null && x_axis_matches.length > 1) {
            x_axis = 1;
          }
          x_axis_matches = /"xAxisOption":"(_ALPHABETICAL)"/.exec(state_string);
          if (x_axis_matches != null && x_axis_matches.length > 1) {
            x_axis = 100;
          }

          // Determine the Y axis type.
          y_axis = 2;
          y_axis_matches = /"yAxisOption":"([0-9]+)"/.exec(state_string);
          if (y_axis_matches != null && y_axis_matches.length > 1) {
            y_axis = parseInt(y_axis_matches[1]);
          }
          y_axis_matches = /"yAxisOption":"(_TIME)"/.exec(state_string);
          if (y_axis_matches != null && y_axis_matches.length > 1) {
            y_axis = 1;
          }
          y_axis_matches = /"yAxisOption":"(_ALPHABETICAL)"/.exec(state_string);
          if (y_axis_matches != null && y_axis_matches.length > 1) {
            y_axis = 100;
          }

          // Find the selected models, and display the visual model.
          selected_models = getSelectedModels(chart);
          if (selected_models.length == 0) {
            if (num_models == 1) {
              selected_models = [];
              for (var model in all_data) {
                selected_models.push(model);
              }
            } else {
              drawVisualDisplay(["--"], -1);
              return;
            }
          }

          // Draw the parameter comparison table.
          drawParameterComparatorChart(x_axis-1, y_axis-1, selected_models);

          // Draw the visual model of the first selected model.
          drawVisualDisplay(selected_models, current_time);
        });
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

      function drawParameterComparatorChart(x_axis_index, y_axis_index,
                                            models) {
        var data = new google.visualization.DataTable();

        // If there are no selected models, or either of the parameters chosen
        // as the X or Y axis are not ones that can be compared (above 5), don't
        // display anything.
        if (models.length == 0 || models[0] == "--" ||
            x_axis_index > 5 || y_axis_index > 5) {
          data.addColumn('number', 'Nothing');
          data.addColumn('number', 0);
          new google.visualization.ScatterChart(
              document.getElementById('parameter_chart_div')).
            draw(data,
                {title: "Model: ''",
                 width:1, height:1,
                 legend: {position: 'none'},
            });
          return;
        }

        // Determine the axis field names and titles.
        x_axis = data_field_names[x_axis_index];
        x_axis_title = data_field_titles[x_axis];
        y_axis = data_field_names[y_axis_index];
        y_axis_title = data_field_titles[y_axis];

        data.addColumn('number', x_axis);
        for (var model in models) {
          data.addColumn('number', models[model]);
        }

        for (var i = 0; i < models.length; ++i) {
          var model = models[i];
          var model_data = all_data[model];
          for (var j in model_data) {
            event_data = model_data[j];
            row_data = [event_data[x_axis]];
            for (var k = 0; k < models.length; ++k) {
              if (k == i) {
                row_data.push(event_data[y_axis]);
              } else {
                row_data.push(null);
              }
            }
            data.addRow(row_data);
          }
        }

        // Create and draw the visualization.
        var models_title = "Model: '" + models[0] + "'";
        if (models.length > 1) {
          models_title = "Models: ";
          for (var model in models) {
            models_title += models_title + "'" + models[model] + "' ";
          }
        }
        new google.visualization.ScatterChart(
            document.getElementById('parameter_chart_div')).
          draw(data,
               {title: models_title,
                width: parseInt(winW*0.5), height: parseInt(winH*0.5),
                vAxis:  {title: y_axis_title},
                hAxis:  {title: x_axis_title},
                legend: {position: 'right'}});
      }

      function drawVisualDisplay(models, time) {
        var img = document.getElementById("viz_display_img");
        var title = document.getElementById("viz_display_title");

        if (models.length == 0 || models[0] == "--" || time < 0) {
          img.width = 0;
          img.height = 0;
          img.src = "//:0";
          img.alt = "";
          title.innerHTML = "";
        } else {
          model = models[0];
          img.width = parseInt(winW*0.5);
          img.height = parseInt(winH*0.5);
          img.src = viz_data[model][time];
          img.alt = model + "[" + time + "]: " + viz_data[model][time].file;
          title.innerHTML = "'" + model + "' (time: " + time + ")";
        }
      }
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
            <img name='viz_display_img' id="viz_display_img" src="//:0" width=0 height=0 alt=""/>
            <span id="viz_display_title"/>
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <div id="parameter_chart_div"/>
        </td>
      </tr>
    </table>
  </body>
</html>
