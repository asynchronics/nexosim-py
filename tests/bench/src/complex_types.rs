use nexosim::ports::Output;
use nexosim::{model::Model, Message};
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize, Message)]
pub enum TestLoad {
    VarA(),
    VarB {},
    VarC(i32),
    VarD(String, f64),
    VarE { x: String, y: bool },
    VarF(TestSubLoad),
    VarG { x: i32, y: TestSubLoad },
}

#[derive(Clone, Serialize, Deserialize, Message)]
pub enum TestSubLoad {
    VarA,
    VarB {},
    VarC(i32),
    VarD(String, f64),
    VarE { x: String, y: bool },
}

/// MyModel.
#[derive(Default)]
pub(crate) struct MyModel {
    pub(crate) output: Output<TestLoad>,
}

impl MyModel {
    pub async fn my_input(&mut self, value: TestLoad) {
        self.output.send(value).await;
    }
}

impl Model for MyModel {}
