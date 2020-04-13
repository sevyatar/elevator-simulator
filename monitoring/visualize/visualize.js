var margin = 10;
var floor_height = 50;
var floor_width = 200;

var elevator_height = 40;
var elevator_width = 40;

var current_event_index = -1;

var floors_count = data["floors"];
var initial_floor = data["initial_floor"];
var current_floor = initial_floor;

var canvas_element = document.getElementById("my_canvas");
canvas_element.width  = window.innerWidth;
canvas_element.height = window.innerHeight;

var timestamp_display_element = document.getElementById("timestamp_display");
var event_index_display_element = document.getElementById("event_index_display");
var event_display_element = document.getElementById("event_display");
var forward_btn = document.getElementById("forward");

var canvas = new fabric.Canvas('my_canvas');

function floor_to_elevator_y(floor) {
    return margin + (floor_height * (floor - 1)) + ((floor_height - elevator_height) / 2);
}

function draw_initial_state() {
    // Create floors
    floor_rider_counter_map = {};
    for (let i=1; i <= floors_count; i++) {
        var font_size = 20;
        var floor_number_text = new fabric.Text('' + i, {
            top: (floor_height - font_size) / 2,
            fontSize: font_size,
            hasControls: false,
            hasBorders: false,
            lockMovementX: true,
            lockMovementY: true
        });

        var floor = new fabric.Rect({
            left: 40,
            width: floor_width,
            height: floor_height,
            fill: 'rgba(0,0,0,0)',
            stroke: 'black',
            strokeWidth: 1,
            hasControls: false,
            hasBorders: false,
            lockMovementX: true,
            lockMovementY: true
        });

        var floor_riders_count = new fabric.Text('0', {
            top: (floor_height - font_size) / 2,
            left: floor.left + (floor.width / 2),
            fontSize: font_size,
            hasControls: false,
            hasBorders: false,
            lockMovementX: true,
            lockMovementY: true
        });

        var floor_group = new fabric.Group([floor_number_text, floor, floor_riders_count], {
            left: margin,
            top: margin + ((i - 1) * floor_height),
            hasControls: false,
            hasBorders: false,
            lockMovementX: true,
            lockMovementY: true
        });
        canvas.add(floor_group);

        floor_rider_counter_map[i] = floor_riders_count;
    }

    // Create the elevator
    var elevator_rect = new fabric.Rect({
        fill: 'orange',
        stroke : 'black',
        width: elevator_width,
        height: elevator_height,
        hasControls: false,
        hasBorders: false,
        lockMovementX: true,
        lockMovementY: true
    });

    elevator_riders_count = new fabric.Text('0', {
        top: (elevator_height - font_size) / 2,
        left: (elevator_width - font_size) / 2,
        fontSize: font_size,
        hasControls: false,
        hasBorders: false,
        lockMovementX: true,
        lockMovementY: true
    });

    // Ugliness ahead: I'm adding all those spaces to make sure there's enough room for the text later on.
    elevator_event_text = new fabric.Text('                            ', {
        top: (elevator_height - font_size) / 2,
        left: elevator_width + 10,
        fontSize: font_size,
        hasControls: false,
        hasBorders: false,
        lockMovementX: true,
        lockMovementY: true
    });

    elevator = new fabric.Group([elevator_rect, elevator_riders_count, elevator_event_text], {
        left: floor_group.width + 30,
        top: floor_to_elevator_y(initial_floor),
        hasControls: false,
        hasBorders: false,
        lockMovementX: true,
        lockMovementY: true
    });

    canvas.add(elevator);
    canvas.renderAll();
}

function increase_text_element(element) {
    var new_count = parseInt(element.text) + 1;
    element.set('text', '' + new_count);

    if (new_count > 0) {
        element.setColor('red');
    }

    canvas.renderAll();
}

function decrease_text_element(element) {
    var new_count = parseInt(element.text) - 1;
    element.set('text', '' + new_count);

    if (new_count <= 0) {
        element.setColor('black');
    }

    canvas.renderAll();
}

function render_request(source_floor) {
    increase_text_element(floor_rider_counter_map[source_floor]);
}

function render_pickup(floor) {
    decrease_text_element(floor_rider_counter_map[floor]);
    increase_text_element(elevator_riders_count);
    elevator_event_text.set('text', 'PICKUP');
    elevator_event_text.setColor("blue");
}

function render_dropoff(floor) {
    decrease_text_element(elevator_riders_count);
    elevator_event_text.set('text', 'DROPOFF');
    elevator_event_text.setColor("red");
}

function visualize_elevator_movement(previous_floor, current_floor) {
    var floors_per_second = 10;

    var floor_diff = Math.abs(current_floor - previous_floor);
    var movement_duration_ms = floor_diff / floors_per_second * 1000;

    forward_btn.disable = true;
    elevator.animate('top', floor_to_elevator_y(current_floor), {
      duration: movement_duration_ms,
      onChange: canvas.renderAll.bind(canvas),
      onComplete: function() {forward_btn.disabled = false;},
    });
}

function render_event(event_type, event_floor) {
    switch(event_type) {
        case "REQUEST":
            render_request(event_floor);
            break;
        case "PICKUP":
            render_pickup(event_floor);
            break;
        case "DROPOFF":
            render_dropoff(event_floor);
            break;
        case "FLOOR_PASSED":
            // No need to do anything
            break;
        default:
            break;
    }

    canvas.renderAll();
}

function draw_event() {
    var event = data.events[current_event_index];
    var event_floor = event.event_floor;
    var previous_floor = current_floor;

    current_floor = event.elevator_floor;

    // Reset elevator event text
    elevator_event_text.set('text', '');

    // Update controls display
    timestamp_display_element.innerHTML = event.ts;
    event_index_display_element.innerHTML = current_event_index + ' / ' + data.events.length;
    event_display.innerHTML = JSON.stringify(event);

    // Move elevator
    visualize_elevator_movement(previous_floor, current_floor);

    render_event(event.event_type, event_floor);
}

function step_forward() {
    current_event_index += 1;
    if (current_event_index >= data.events.length) {
        alert("No more steps!");
        return;
    }

    draw_event();
}

draw_initial_state();
