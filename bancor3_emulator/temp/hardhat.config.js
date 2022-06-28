require("@nomiclabs/hardhat-truffle5");

module.exports = {
    solidity: {
        version: "0.8.13",
        settings: {
            optimizer: {
                enabled: true,
                runs: 200
            }
        }
    },
    paths: {
        sources: "./project/contracts",
        tests: "./project/tests",
        cache: "./project/cache",
        artifacts: "./project/artifacts"
    },
    mocha: {
        useColors: true,
        enableTimeouts: false,
        timeout: 1000000000,
        reporter: "list" // https://mochajs.org/#reporters
    }
};
