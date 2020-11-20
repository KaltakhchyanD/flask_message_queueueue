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
        let data = await response.text();
        return data;
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

        let old_html = $("#task_created").children("#task_created").html();
        $("#task_created").children("#task_created").html(old_html+data_html);
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
        //this.initializeCheckResultButtonEvent();
    }

    async start_task_button_action(evt, button){
        evt.preventDefault();
        try {
            let task_id = uuidv4();
            // !!!
            let create_json = {
                "message":$("#messageInput").val(),
                "task_id":task_id,
            }
            let response = await this.model.start_task(create_json);

            console.log(response)
            this.view.show_task_been_created(task_id);
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