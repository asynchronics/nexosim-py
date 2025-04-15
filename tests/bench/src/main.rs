//! Tool for starting a nexosim server set up with a test bench.

use async_std::prelude::StreamExt;

use signal_hook::consts::TERM_SIGNALS;
use signal_hook_async_std::Signals;

use clap::Parser;
use grpc_python::sims;
use nexosim::server;

/// Start a nexosim server set up with a test bench.
#[derive(Parser)]
#[command(about)]
struct Cli {
    /// The bench the server will be set up with.
    bench: Bench,

    /// Start a http server instead of the default local unix server.
    #[arg(long)]
    http: bool,

    /// Set the address of the server.
    #[arg(short, long)]
    address: Option<String>,
}

#[derive(Debug, Clone, Copy)]
enum Bench {
    Coffee,
    CoffeeRt,
    Types,
}

impl std::str::FromStr for Bench {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "coffee" => Ok(Self::Coffee),
            "coffeert" => Ok(Self::CoffeeRt),
            "types" => Ok(Self::Types),
            _ => Err(format!("{s} bench not recognized.")),
        }
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    let addr = match cli.address {
        None => {
            if cli.http {
                String::from("0.0.0.0:41633")
            } else {
                String::from("/tmp/nexo")
            }
        }
        Some(value) => value,
    };

    let mut signals = Signals::new(TERM_SIGNALS)?;
    let signal = async move {
        signals.next().await;
    };

    if cli.http {
        match cli.bench {
            Bench::Coffee => {
                println!("HTTP Coffee server listening at {}", addr);
                server::run_with_shutdown(sims::coffee_bench, addr.parse()?, signal)
            }
            Bench::CoffeeRt => {
                println!("HTTP CoffeeRT server listening at {}", addr);
                server::run_with_shutdown(sims::rt_coffee_bench, addr.parse()?, signal)
            }
            Bench::Types => {
                println!("HTTP Bench2 server listening at {}", addr);
                server::run_with_shutdown(sims::types_bench, addr.parse()?, signal)
            }
        }?;
    } else {
        #[cfg(unix)]
        match cli.bench {
            Bench::Coffee => {
                println!("Local Coffee server listening at {}", addr);
                server::run_local_with_shutdown(sims::coffee_bench, addr, signal)
            }
            Bench::CoffeeRt => {
                println!("Local CoffeeRT server listening at {}", addr);
                server::run_local_with_shutdown(sims::rt_coffee_bench, addr, signal)
            }
            Bench::Types => {
                println!("Local Bench2 server listening at {}", addr);
                server::run_local_with_shutdown(sims::types_bench, addr, signal)
            }
        }?;

        #[cfg(not(unix))]
        return Err("Run with the --http arg on non-unix systems.");
    }

    println!("Server exited");
    Ok(())
}
