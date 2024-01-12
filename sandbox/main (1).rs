//main.rs
use reqwest::Error;
use std::time::SystemTime;
use serde_json;
// use serde_json::{Deserialize, Serialize};

fn get_sys_time_in_msecs() -> u128 {
    match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        Ok(n) => n.as_millis(),
        Err(_) => panic!("SystemTime before UNIX EPOCH!"),
    }
}
fn get_sys_time_in_secs() -> u64 {
    match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        Ok(n) => n.as_secs(),
        Err(_) => panic!("SystemTime before UNIX EPOCH!"),
    }
}


#[derive(serde::Serialize, serde::Deserialize, Debug)]
struct Data {
    time: String,
    speed: String,
    distance: String
}

async fn post_request(x:u8, ) -> Result<(), Error> {
    let url = format!("http://localhost:8000/items/{}", x);
    let time = get_sys_time_in_msecs();
    let distance = get_sys_time_in_secs().to_string();
    let speed = time.to_string().chars().last().unwrap();
    // let json_data = r#"{"time": "{time}","speed": "123","distance": "123"}"#;
    let data = Data{
        time: time.to_string().to_owned(),
        speed: speed.to_string().to_owned(),
        distance: distance.to_owned()
        };
    let json_data = serde_json::to_string(&data).unwrap();
    
    let client = reqwest::Client::new();

    let response = client
        .post(url)
        .header("Content-Type", "application/json")
        .body(json_data)
        .send()
        .await?;
    println!("Status code: {}", response.status());
    Ok(())

}

#[tokio::main]
async fn main() -> Result<(), Error> {
    loop {
          for x in 0..10{
            post_request(x).await?;
    }  
    }
    Ok(())
}