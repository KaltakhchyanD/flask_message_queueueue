class Model {

    async start_task() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        // Call the REST endpoint and wait for data
        let endpoint_url = "/rabbit_create";
        let response = await fetch(endpoint_url, options);
        let data = await response.text();
        return data;
    }

    async check_result() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        // Call the REST endpoint and wait for data
        let endpoint_url = "/rabbit_result_blocking";
        let response = await fetch(endpoint_url, options);
        let data = await response.json();
        return data;
    }

}

let seconds = 0;
let some_id = 0;

class View {
    //seconds = 0;
    //some_id = 0;

    constructor(){
        //this.seconds = 0;
        //console.log('At constr -' + this.seconds);
        //this.some_id = 0;
        console.log('Global in consr - '+seconds);
    }

    show_task_been_created(){
        let current_path = window.location.href.split("?")[0];
        let data_html ="<br>"
        data_html+= "<h3>Task has been successfully created!</h3>" 
        $("#task_created").html(data_html);
    }


    show_final_result(result_message){

        let current_path = window.location.href.split("?")[0];
        let data_html ="<br>"
        data_html+= "<h3>Here is final result</h3>" 
        data_html+=result_message
        data_html+="<br>"
        $("#final_result").html(data_html);
    }

    increment_seconds(){
        //this.seconds+=1;
        //console.log(this.seconds);
        seconds+=1;
        console.log(seconds);
    }

    start_timer(){
        some_id = setInterval(this.increment_seconds, 1000);
    }

    stop_timer(){
        clearInterval(some_id);
    }

    clear_timer(){
        seconds = 0;
    }

    view_timer(){
        $("#stop_clock").text('Task took roughly about '+seconds+' seconds');

    }

}

class Controller{
    constructor(model, view) {
        this.model = model;
        this.view = view;
        this.initialize();
    }

    async initialize() {
        this.initializeButtonEvent();
        this.initializeCheckResultButtonEvent();
    }

    async start_task_button_action(evt, button){
        evt.preventDefault();
        try {   
            let response = await this.model.start_task();
            console.log(response)
            console.log('Seconds at start - ');
            console.log(seconds);
            this.view.show_task_been_created();
            this.view.start_timer();
        } catch(err) {
            console.log(err)
        }
    }

    async check_result_button_action(evt, button){
        evt.preventDefault();
        try {   
            let response = await this.model.check_result();
            console.log(response)

            if (response['status']==='Pending'){
                this.view.show_final_result('Pending');
            } else {
                this.view.show_final_result(response['message']);
                console.log(seconds);
                this.view.stop_timer();
                this.view.view_timer();
                this.view.clear_timer();

            }

        } catch(err) {
            console.log(err)
        }
    }


    initializeButtonEvent(){
        let send_buttons = $( ":button[name^='StartTask']" );
        for (const some_button of send_buttons){
            some_button.addEventListener ("click", (evt) =>this.start_task_button_action(evt, some_button));
        }
    }

    initializeCheckResultButtonEvent(){
        let send_buttons = $( ":button[name^='CheckResult']" );
        for (const some_button of send_buttons){
            some_button.addEventListener ("click", (evt) =>this.check_result_button_action(evt, some_button));
        }
    }

}


// Create the MVC components
const model = new Model();
const view = new View();
const controller = new Controller(model, view);

// export the MVC components as the default
export default {
    model,
    view,
    controller
};