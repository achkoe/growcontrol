class Button {
    constructor(btnState) {
        this.btnState = btnState;
        this.btnState.addEventListener("click", this.toggle_on_off.bind(this));
    }
    
    toggle_on_off() {
        if (this.btnState.textContent === 'Off') {
            this.btnState.textContent = 'On';
            this.btnState.classList.remove('off');
            this.btnState.classList.add('on');
        } else {
            this.btnState.textContent = 'Off';
            this.btnState.classList.remove('on');
            this.btnState.classList.add('off');
        }
    }
    
    update(data) {

    }
}

class ConnectedButton extends Button {
    constructor(btnControl, btnState) {
        super(btnState);
        this.btnControl = btnControl;
        const self = this;

        this.btnControl.addEventListener("click", this.toggle_auto_manual.bind(this));
    }

    toggle_auto_manual() {
        console.log(this);
        if (this.btnControl.textContent === 'Auto' ) {
            this.btnControl.textContent = 'Manual';
            this.btnControl.classList.remove('auto');
            this.btnControl.classList.add('manual');
            this.btnState.disabled = false;
        } else {
            this.btnControl.textContent = 'Auto' ;
            this.btnControl.classList.remove('manual');
            this.btnControl.classList.add('auto');
            this.btnState.disabled = true;
        }
    }


    update(data) {

    }
}

const fanExhaustAir = null;
const cFan = null;
const cHeater = null;
const cLight = null;
const oPump  = {};

document.addEventListener("DOMContentLoaded", function() {
    const fanExhaustAir = new Button(document.getElementById('fanExhaustAirOnOff'));
    const cFan = new ConnectedButton(document.getElementById("fan_mode"), document.getElementById("fanOnOffToggle"));
    const cHeater = new ConnectedButton(document.getElementById("heater_mode"), this.getElementById("heaterOnOffToggle"));
    const cLight = new ConnectedButton(document.getElementById("light_mode"), this.getElementById("lightToggle"));
    
    for (let index = 1; index < 10; index++) {
        pumpToggle = document.getElementById("pumpToggle_" + index);
        if (pumpToggle == null) break;
        oPump[index] = new ConnectedButton(pumpToggle, document.getElementById("pumpOnOffToggle_" + index));
    }
});