class Model {

    async start_task(message_json) {
        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(message_json)
        };
        // Call the REST endpoint and wait for data
        let endpoint_url = "/rabbit_create";
        let response = await fetch(endpoint_url, options);
        let data = await response.text();
        return data;
    }

    async check_result(task_id) {

        let create_json = {
                "task_id":task_id
            } 

        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(create_json)
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

let tasks_sent = 0;
let responses_received = 0;

class View {

    constructor(){
        console.log('Global in consr - '+seconds);
    }
    
    show_number_tasks(){
        $("#number_tasks_sent").text('Task been sent: '+tasks_sent);
    }

    show_number_responses(){
        $("#number_responses_received").text('Responses been received: '+responses_received);
    }

    show_status_pending(task_id) {
        let current_path = window.location.href.split("?")[0];

        let data_html = "<div id="+task_id+">";

        data_html+="<br>"
        data_html+= "<h3>Status is pending, wait a bit</h3>" 
        data_html+="<br>"
        data_html+= "</div>"

        $("#"+task_id).html(data_html);
    }

    show_task_been_created(task_id){
        let current_path = window.location.href.split("?")[0];

        let data_html = "<div class=\"task_created\" id="+task_id+">";
        data_html+="<br>"
        data_html+= "<h3>Task has been successfully created!</h3>" 
        data_html+="<br>"
        data_html+= "</div>"

        let old_html = $("#task_created").html();
        $("#task_created").html(old_html+data_html);
    }

    //clear_task_been_created(){
    //    $("#task_created").html("");
    //}

    show_final_result(result_message, task_id){
        let current_path = window.location.href.split("?")[0];
        let data_html ="<br>"
        data_html+= "<h3>Here is final result</h3>" 
        data_html+=result_message
        data_html+="<br>"
        $("#"+task_id).html(data_html);
    }

    //clear_final_result(){
    //    let current_path = window.location.href.split("?")[0];
    //    $("#final_result").html("");
//
    //}

    increment_seconds(){
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

    clear_timer_result(){
        $("#stop_clock").text('');
    }

}


function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
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
            let task_id = uuidv4();
            let create_json = {
                "message":$("#messageInput").val()+' #'+tasks_sent,
                "task_id":task_id
            }   
            let response = await this.model.start_task(create_json);

            console.log(response)
            this.view.show_task_been_created(task_id);
            //this.view.clear_final_result();
            //this.view.clear_timer_result();
            tasks_sent++;
            this.view.show_number_tasks();
        } catch(err) {
            console.log(err)
        }
    }

    async check_result_button_action(evt, button){
        evt.preventDefault();
        try {   

            // Set all tasks to pending
            let ids_of_tasks = [];

            $(".task_created").each(function() {
                console.log($(this).attr('id'));
                ids_of_tasks.push($(this).attr('id'));
                $(this).addClass('task_pending').removeClass('task_created');
            });     

            // Нужна проверка на непустоту списка ids_of_tasks
            // Иначе будет ошибка на shift()

            if (ids_of_tasks.length === 0) {
                console.log('No new tasks been sent!!!')
                return
            }

            for (const some_id of ids_of_tasks){
                this.view.show_status_pending(some_id);
            }

            console.log('Counters b4: '+responses_received+" "+tasks_sent);
            while(responses_received<tasks_sent){

                
                let id_to_get_response = ids_of_tasks.shift();
                let response = await this.model.check_result(id_to_get_response);
                

                console.log(response);
                responses_received++;
                this.view.show_number_responses();
                console.log("Task id from back - "+response['task_id']);

                this.view.show_final_result(response['message'], response['task_id']);
            }
            console.log('Counters after: '+responses_received+" "+tasks_sent);


            //this.view.clear_task_been_created();
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