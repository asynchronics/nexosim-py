//! Tool for starting a nexosim server set up with a test bench.
use nexosim::server;
use clap::Parser;
use grpc_python::sims;

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
    address: Option<String>
}

#[derive(Debug, Clone, Copy)]
enum Bench {
    Coffee,
    CoffeeRT,
    Bench2,
}

impl std::str::FromStr for Bench {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "coffee" => Ok(Self::Coffee),
            "coffeert" => Ok(Self::CoffeeRT),
            "bench2" => Ok(Self::Bench2),
            _ => Err(format!("{s} bench not recognized.")),
        }
    }
}

fn main() {
    let cli = Cli::parse();

    let addr = match cli.address {
        None => {
            if cli.http {
                String::from("0.0.0.0:41633")
            } else {
                String::from("/tmp/nexo")
            }
        } 
        Some(value) => {
            value
        }
    };

    if cli.http{
        match cli.bench {
            Bench::Coffee => {
                println!("HTTP Coffee server listening at {}", addr);
                server::run(sims::coffee_bench, addr.parse().unwrap())
            },
            Bench::CoffeeRT => {
                println!("HTTP CoffeeRT server listening at {}", addr);
                server::run(sims::rt_coffee_bench, addr.parse().unwrap())
            },
            Bench::Bench2 => {
                println!("HTTP Bench2 server listening at {}", addr);
                server::run(sims::bench_2, addr.parse().unwrap())
            }
        }.unwrap();
    } else {
        match cli.bench {
            Bench::Coffee => {
                println!("Local Coffee server listening at {}", addr);
                server::run_local(sims::coffee_bench, addr)
            },
            Bench::CoffeeRT => {
                println!("Local CoffeeRT server listening at {}", addr);
                server::run_local(sims::rt_coffee_bench, addr)
            },
            Bench::Bench2 => {
                println!("Local Bench2 server listening at {}", addr);
                server::run_local(sims::bench_2, addr)
            }
        }.unwrap();
    }
}