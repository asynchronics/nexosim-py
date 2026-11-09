//! Bench used by the documentation examples.

use nexosim::model::Model;
use nexosim::ports::Output;
use nexosim::Message;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct ModelConfig {
    pub foo: u16,
    pub bar: String,
}
#[derive(Clone, Serialize, Deserialize, Message)]
pub struct OutputEvent {
    pub foo: u16,
    pub bar: String,
}

#[derive(Serialize, Deserialize, Default)]
pub struct MyModel {
    pub output: Output<OutputEvent>,
    foo: u16,
    bar: String,
    count: u16,
}

#[Model]
impl MyModel {
    pub fn new(cfg: Option<ModelConfig>) -> Self {
        let ModelConfig { foo, bar } = cfg.unwrap_or(ModelConfig {
            foo: 0,
            bar: String::from("string"),
        });
        Self {
            foo,
            bar,
            ..Default::default()
        }
    }

    pub async fn my_input(&mut self, value: u16) {
        self.count += value;
        let event = OutputEvent {
            foo: value,
            bar: self.bar.clone(),
        };
        self.output.send(event).await;
    }

    pub async fn my_replier(&mut self) -> String {
        self.bar.clone()
    }

    pub async fn to_string(&mut self, value: u16) -> String {
        value.to_string()
    }

    pub async fn count(&mut self) -> u16 {
        self.count
    }
}

#[derive(Serialize, Deserialize, Default)]
pub(crate) struct AddOne {
    pub(crate) output: Output<u16>,
}

#[Model]
impl AddOne {
    pub async fn input(&mut self, value: u16) {
        self.output.send(value + 1).await;
    }
}
