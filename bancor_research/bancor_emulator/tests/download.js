const fs = require("fs");
const https = require("https");

const DIR_NAME = "project/tests/data";

if (!fs.existsSync(DIR_NAME)) {
    fs.mkdirSync(DIR_NAME);
}

function download(fileNames) {
    if (fileNames.length > 0) {
        const fileName = `${fileNames[0]}.json`;
        console.log(`Downloading ${fileName}`);
        const file = fs.createWriteStream(`${DIR_NAME}/${fileName}`);
        https.get(`https://raw.githubusercontent.com/bancorprotocol/contracts-v3/dev/test/data/${fileName}`, function (response) {
            response.pipe(file);
            file.on("finish", function () {
                file.close();
                download(fileNames.slice(1));
            });
        });
    }
}

download([
    "BancorNetworkSimpleFinancialScenario1",
    "BancorNetworkSimpleFinancialScenario2",
    "BancorNetworkSimpleFinancialScenario3",
    "BancorNetworkSimpleFinancialScenario4",
    "BancorNetworkSimpleFinancialScenario5",
    "BancorNetworkSimpleFinancialScenario6",
    "BancorNetworkComplexFinancialScenario1",
    "BancorNetworkComplexFinancialScenario2",
    "BancorNetworkRewardsFinancialScenario1",
    "BancorNetworkRewardsFinancialScenario2",
    "PoolCollectionWithdrawalCoverage1",
    "PoolCollectionWithdrawalCoverage2",
    "PoolCollectionWithdrawalCoverage3",
    "PoolCollectionWithdrawalCoverage4",
    "PoolCollectionWithdrawalCoverage5",
    "PoolCollectionWithdrawalCoverage6",
    "PoolCollectionWithdrawalCoverage7",
    "PoolCollectionWithdrawalCoverage8",
]);
