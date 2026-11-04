use nexosim::model::Model;
use nexosim::ports::Output;
use nexosim::Message;
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

#[derive(Clone, Serialize, Deserialize, Message)]
pub enum UnitEnum {
    VarA,
    VarB,
}

#[derive(Clone, Serialize, Deserialize, Message)]
pub struct Partial {
    unit: Option<UnitEnum>,
    load: Option<TestLoad>,
}

/// MyModel.
#[derive(Default, Deserialize, Serialize, Debug)]
pub(crate) struct MyModel {
    pub(crate) output: Output<TestLoad>,
    pub(crate) partial_output: Output<Partial>,
}

#[Model]
impl MyModel {
    pub async fn my_input(&mut self, value: TestLoad) {
        self.output.send(value).await;
    }

    pub async fn partial_input(&mut self, partial: Partial) {
        self.partial_output.send(partial).await;
    }
}
