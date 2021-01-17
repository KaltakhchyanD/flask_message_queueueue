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
        let endpoint_url = "/celery_create_task";
        let response = await fetch(endpoint_url, options);

        return response;
    }

    async check_result(message_json) {
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
        let endpoint_url = "/celery_check_result";
        let response = await fetch(endpoint_url, options);
        return response;
    }
}


class View {
    constructor(){
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

    show_pending(task_id){
        let data_html = "<div class=\"task_pending\" id="+task_id+">";
        data_html+="<br>"
        data_html+= "<h3>Task status: Pending</h3>" 
        data_html+="<br>"
        data_html+= "</div>"

        $("#"+task_id).html(data_html);
    }

    show_error_task(task_id){
        let data_html = "<div class=\"task_pending\" id="+task_id+">";
        data_html+="<br>"
        data_html+= "<h3>Task status: Error</h3>" 
        data_html+="<br>"
        data_html+= "</div>"

        $("#"+task_id).html(data_html);
    }

    show_task_is_ready(task_id, message){
        //console.log("IN show ready with "+task_id+" and "+message);
        let data_html = "<div class=\"task_pending\" id="+task_id+">";
        data_html+="<br>"
        data_html+= "<h3>Task status: Finnish</h3>" 
        data_html+= "<h3>Message: "+message+"</h3>" 
        data_html+="<br>"
        data_html+= "</div>"
        $("#"+task_id).html(data_html);
    }

    show_custom_error(message){
        let data_html ="<br>"
        data_html+="<h4>"+message+"</h4>"
        data_html+="<br>"
        $("#error_message").html(data_html);
    }

    clear_custom_error(message){
        let data_html =""
        $("#error_message").html(data_html);
    }

}


function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}


function get_error_message_by_code(error_json){
    let error_code = error_json["error_code"];
    let error_message = '';

    if (error_code==1 || (5<=error_code && error_code<=8)) {
        error_message = "All parameters are necessery";
    } else if (2<=error_code && error_code<=4){
        error_message = error_json["error_message"];
    
    } else if (10<=error_code && error_code<=12){
        error_message = error_json["error_message"];
    }  else{
        error_message = "Something went wrong";
    }
    return error_message;
}


let pending_tasks_id = []

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
                "message":$("#messageInput").val(),
                "quantity":$("#numberOfTasks").val(),
                "priority":$("#prioritySelect").val(),
                "task_id":task_id,
            }
            let response = await this.model.start_task(create_json);
            console.log(response);

            if (response['status']==400) {
                let error_json = await response.json();
                let error_message = get_error_message_by_code(error_json);

                this.view.show_custom_error(error_message);

            } else if (response['status']==200){
                this.view.clear_custom_error();
                pending_tasks_id.push(task_id);
                this.view.show_task_been_created(task_id);
            }

        } catch(err) {
            console.log(err)
        }
    }

    async check_result_button_action(evt, button){
        evt.preventDefault();
        try {

            // Make all tasks pending and show it
            for (let task_id of pending_tasks_id){
                this.view.show_pending(task_id);
            }

            // Iterate over pending tasks list
            // If its ready - show it
            // then increment counter
            let tasks_to_delete_from_local_queue = 0;
            for (let task_id of pending_tasks_id){
                let check_result_json = {'task_id':task_id};
                let response = await this.model.check_result(check_result_json);

                console.log("response status is "+ response['status']);
                console.log(response);
                if (response['status']==400||response['status']==500) {
                    let error_json = await response.json();
                    let error_message = get_error_message_by_code(error_json);
                    tasks_to_delete_from_local_queue++;
                    this.view.show_custom_error(error_message);
                    this.view.show_error_task(task_id);

                    
                } else if (response['status']==200){
                    let response_json = await response.json();

                    if (response_json["status"]==="Ready"){
                        this.view.show_task_is_ready(task_id, response_json["message"]);
                        tasks_to_delete_from_local_queue++;
                    }


                }
            }

            // Remove first n tasks from pending tasks list
            // where n == num of tasks ready or missing at server
            // so its ok to shift em
            // Just need to show proper error message to user
            for(let i=0; i<tasks_to_delete_from_local_queue; i++){
                pending_tasks_id.shift();
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