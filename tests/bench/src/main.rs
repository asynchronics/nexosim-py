//! Tool for starting a nexosim server set up with a test bench.

#[cfg(unix)]
use async_std::prelude::StreamExt;
#[cfg(unix)]
use signal_hook::consts::TERM_SIGNALS;
#[cfg(unix)]
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
    CoffeeRtTicker,
    Payload,
    Docs,
    DocsRt,
}

impl std::str::FromStr for Bench {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "coffee" => Ok(Self::Coffee),
            "coffeert" => Ok(Self::CoffeeRt),
            "coffeertticker" => Ok(Self::CoffeeRtTicker),
            "payload" => Ok(Self::Payload),
            "docs" => Ok(Self::Docs),
            "docsrt" => Ok(Self::DocsRt),
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

    #[cfg(unix)]
    let signal = {
        let mut signals = Signals::new(TERM_SIGNALS)?;
        async move {
            signals.next().await;
        }
    };
    #[cfg(not(unix))]
    let signal = std::future::pending::<()>();

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
            Bench::CoffeeRtTicker => {
                println!("HTTP CoffeeRT with Ticker server listening at {}", addr);
                server::run_with_shutdown(sims::rt_coffee_bench_ticker, addr.parse()?, signal)
            }
            Bench::Payload => {
                println!("HTTP Payload server listening at {}", addr);
                server::run_with_shutdown(sims::payload_bench, addr.parse()?, signal)
            }
            Bench::Docs => {
                println!("HTTP Docs server listening at {}", addr);
                server::run_with_shutdown(sims::docs_bench, addr.parse()?, signal)
            }
            Bench::DocsRt => {
                println!("HTTP DocsRT server listening at {}", addr);
                server::run_with_shutdown(sims::docs_rt_bench, addr.parse()?, signal)
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
            Bench::CoffeeRtTicker => {
                println!("HTTP CoffeeRT with Ticker server listening at {}", addr);
                server::run_with_shutdown(sims::rt_coffee_bench_ticker, addr.parse()?, signal)
            }
            Bench::Payload => {
                println!("Local Payload server listening at {}", addr);
                server::run_local_with_shutdown(sims::payload_bench, addr, signal)
            }
            Bench::Docs => {
                println!("Local Docs server listening at {}", addr);
                server::run_local_with_shutdown(sims::docs_bench, addr, signal)
            }
            Bench::DocsRt => {
                println!("Local DocsRT server listening at {}", addr);
                server::run_local_with_shutdown(sims::docs_rt_bench, addr, signal)
            }
        }?;

        #[cfg(not(unix))]
        return Err("Run with the --http arg on non-unix systems.".into());
    }

    println!("Server exited");
    Ok(())
}
