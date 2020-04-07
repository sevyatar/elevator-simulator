var margin = 10;
var floor_height = 50;
var floor_width = 200;

var elevator_height = 40;
var elevator_width = 40;

var floors = data["floors"];
var initial_floor = data["initial_floor"];

var canvas_element = document.getElementById("my_canvas");
canvas_element.width  = window.innerWidth;
canvas_element.height = window.innerHeight;

var canvas = new fabric.Canvas('my_canvas');

function floor_to_elevator_y(floor) {
    return margin + (floor_height * (floor - 1)) + ((floor_height - elevator_height) / 2);
}

function draw_initial_state() {
    // Create floors
    for (let i=0; i < floors; i++) {
        var font_size = 20;
        var floor_number_text = new fabric.Text('' + (i + 1), {
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

        var floor_group = new fabric.Group([floor_number_text, floor], {
            left: margin,
            top: margin + (i*floor_height),
            hasControls: false,
            hasBorders: false,
            lockMovementX: true,
            lockMovementY: true
        });
        canvas.add(floor_group);
    }

    // Create the elevator
    elevator = new fabric.Rect({
        left: floor_group.width + 30,
        top: floor_to_elevator_y(initial_floor),
        fill: 'orange',
        stroke : 'black',
        width: elevator_width,
        height: elevator_height,
        hasControls: false,
        hasBorders: false,
        lockMovementX: true,
        lockMovementY: true
    });

    canvas.add(elevator);
}

draw_initial_state();
