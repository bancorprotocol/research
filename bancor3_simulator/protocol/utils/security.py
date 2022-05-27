# coding=utf-8
def getContracttokenDictionary():
    """
    @Dev
    Returns the tokenContract : TKN dictionary.
    """
    contractTokenDictionary = {
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" : "eth",
        "0x6B175474E89094C44Da98b954EedeAC495271d0F" : "dai",
        "0x514910771AF9Ca656af840dff83E8264EcF986CA" : "link",
        "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C" : "bnt"
    }
    return(contractTokenDictionary)

def getEmptyMonitor():
    """
    @Dev
    Returns an empty monitor dictionary.
    """
    monitor = {
        "token deposits" : {
            "block number" : [],
            "transaction hash" : [],
            "token" : [],
            "token amount" : [],
            "ethereum master vault balance" :[],
            "simulated master vault balance" : [],
            "ethereum staking ledger balance" :[],
            "simulated staking ledger balance" : [],
            "ethereum pool token supply" :[],
            "simulated pool token supply" : [],
            "ethereum minted pool token amount" : [],
            "simulated minted pool token amount" : [],
        },
        "withdrawals initiated" :{
            "block number" : [],
            "transaction hash" : [],
            "token" : [],
            "withdrawn token amount": [],
            "ethereum pool token amount" : [],
            "simulated pool token amount" : []
        },
        "bnt deposits" : {
            "block number" : [],
            "transaction hash" : [],
            "bnt amount" : [],
            "ethereum transfered bnbnt amount" : [],
            "simulated transfered bnbnt amount" : [],
            "ethereum minted vbnt amount" : [],
            "simulated minted vbnt amount" : [],
        },
        "trades" : {
            "block number" : [],
            "transaction hash" : [],
            "source token amount" : [],
            "source token" : [],
            "target token" : [],
            "ethereum target token amount" : [],
            "simulated target token amount" : [],
            "ethereum previous bnt liquidity" : [],
            "simulated previous bnt liquidity" : [],
            "ethereum previous tkn liquidity" : [],
            "simulated previous tkn liquidity" : [],
            "ethereum new bnt liquidity" : [],
            "simulated new bnt liquidity" : [],
            "ethereum new tkn liquidity" : [],
            "simulated new tkn liquidity" : [],
            "ethereum implied trading fee" : [],
            "true trading fee" : [],
            "ethereum implied network fee" : [],
            "true network fee" : [],
            "ethereum fee paid by trader" : [],
            "simulated fee paid by trader" : [],
            "ethereum implied fee to staking ledger" : [],
            "simulated fee to staking ledger" : [],
            "ethereum implied bnt to vortex ledger" : [],
            "simulated bnt to vortex ledger" : [],
        }
    }
    return(monitor)



# *** Main Security Functions ***


def contractNetworkFeePPMUpdated(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the newFeePPM event from the contracts.
    """
    newFeePPM = getContractFeePPM(df, index)
    newNetworkFee = contractConvertPPM(newFeePPM)
    changeNetworkFee(newNetworkFee)
    return(None)

def contractTradingFeePPMUpdated(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the TradingFeePPMUpdated event from the contracts.
    """
    newFeePPM = getContractFeePPM(df, index)
    newTradingFee = contractConvertPPM(newFeePPM)
    tokenName = getContractTokenName(df, index)
    changeTradingFee(tokenName, newTradingFee)
    return(None)

def contractDepositingEnabled(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the DepositingEnabled event from the contracts.
    """
    doNothing()
    return(None)

def contractFundingLimits(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the FundingLimits event from the contracts.
    """
    tokenName = getContractTokenName(df, index)
    updatedBntFundingLimit = getContractFundingLimit(df, index)
    changeBntFundingLimit(tokenName, updatedBntFundingLimit)
    return(None)

def contractTradingEnabled(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the DepositingEnabled event from the contracts.
    """
    newStatus = getContractNewStatus(df, index)
    if newStatus == True:
        tokenName = getContractTokenName(df, index)
        tokenDecimals = getContractTokenDecimals(df, index)
        bntVirtualBalance = getContractBntNewLiquidity(df, index)
        tknTokenVirtualBalance = getContractTknNewLiquidity(df, index, tokenDecimals)
        bntFundingLimit = getContractLastBntFundingLimit(tokenName)
        enableTrading(tokenName, bntVirtualBalance, tknTokenVirtualBalance, bntFundingLimit)
    else:
        doNothing()
    return(None)

def contractDepositTkn(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the depositTKN event from the contracts.
    """
    tokenName = getContractTokenName(df, index)
    tokenDecimals = getContractTokenDecimals(df, index)
    tknAmount = getContractTokenAmount(df, index, tokenDecimals)
    (
        contractMasterVaultTknBalance,
        contractStakingLedgerTknBalance,
        contractErc20ContractTknBalance,
        contractBntknAmount) = getContractDepositTknOutputs(df, index, tokenDecimals)
    newTimestamp(blockNumber)
    depositTKN(tknAmount, tokenName, user)
    (
        simulatorMasterVaultTknBalance,
        simulatorStakingLedgerTknBalance,
        simulatorErc20ContractTknBalance,
        simulatorBntknAmount) = getSimulationDepositTknOutputs(tokenName)
    depositTknComparisson(
        blockNumber,
        txHash,
        tokenName,
        tknAmount,
        contractMasterVaultTknBalance, simulatorMasterVaultTknBalance,
        contractStakingLedgerTknBalance, simulatorStakingLedgerTknBalance,
        contractErc20ContractTknBalance, simulatorErc20ContractTknBalance,
        contractBntknAmount, simulatorBntknAmount)
    return(None)

def contractWithdrawalInitiated(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the depositTKN event from the contracts.
    """
    tokenName = getContractTokenName(df, index)
    tokenDecimals = getContractTokenDecimals(df, index)
    withdrawValue = getContractReserveTokenAmount(df, index, tokenDecimals)
    contractPoolTokenAmount = getContractWithdrawalInitiatedOutputs(df, index)
    newTimestamp(blockNumber)
    beginCooldown(withdrawValue, tokenName, user)
    simulatorPoolTokenAmount = getSimulatedWithdrawalInitiatedOutputs()
    withdrawalInitiatedComparisson(
        blockNumber,
        txHash,
        tokenName,
        withdrawValue,
        contractPoolTokenAmount,
        simulatorPoolTokenAmount)
    return(None)

def contractDepositBnt(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the depositTKN event from the contracts.
    """
    bntAmount = getContractBntAmount(df, index)
    contractPoolTokenAmount, contractVbntAmount = getContractDepositBntOutputs(df, index)
    newTimestamp(blockNumber)
    depositBNT(bntAmount, user)
    simulatorPoolTokenAmount, simulatorVbntAmount = getSimulatorDepositBntOutputs()
    depositBntComparisson(
        blockNumber,
        txHash,
        bntAmount,
        contractPoolTokenAmount,
        contractVbntAmount,
        simulatorPoolTokenAmount,
        simulatorVbntAmount)
    return(None)

def contractTrade(df, index, blockNumber, txHash):
    """
    @Dev
    Processes the trade event from the contracts.
    """
    (
        sourceToken,
        sourceTokenAmount,
        targetToken,
        contractTargetTokenAmount,
        contractBntPrevLiquidity,
        contractBntNewLiquidity,
        contractTknPrevLiquidity,
        contractTknNewLiquidity,
        contractFeeAmount,
        impliedTradingFee,
        impliedNetworkFee,
        impliedFeeToStakingLedger,
        impliedBntToVortexLedger) = getContractTradeOutputs(df, index, txHash)
    trade(sourceTokenAmount, sourceToken, targetToken, user)
    (
        trueTradingFee,
        simulatedBntPrevLiquidity,
        simulatedBntNewLiquidity,
        simulatedTknPrevLiquidity,
        simulatedTknNewLiquidity) = getSimulatedTradingPoolVars(sourceToken, targetToken)
    (
        simulatedTargetTokenAmount,
        simulatedFeeToStakingLedger,
        simulatedBntToVortexLedger) = getSimulatedTradingOutputs(targetToken)
    trueNetworkFee = nonUsers["globalProtocolSettings"]["networkFee"][-1]
    simulatedFeeAmount = getSimulatedFeeAmount(
        sourceToken,
        sourceTokenAmount,
        simulatedBntPrevLiquidity,
        simulatedTknPrevLiquidity,
        trueTradingFee)
    tradeComparisson(
    blockNumber,
    txHash,
    sourceTokenAmount,
    sourceToken,
    targetToken,
    contractTargetTokenAmount, simulatedTargetTokenAmount,
    contractBntPrevLiquidity, simulatedBntPrevLiquidity,
    contractTknPrevLiquidity, simulatedTknPrevLiquidity,
    contractBntNewLiquidity, simulatedBntNewLiquidity,
    contractTknNewLiquidity, simulatedTknNewLiquidity,
    impliedTradingFee, trueTradingFee,
    impliedNetworkFee, trueNetworkFee,
    contractFeeAmount, simulatedFeeAmount,
    impliedFeeToStakingLedger, simulatedFeeToStakingLedger,
    impliedBntToVortexLedger, simulatedBntToVortexLedger)
    return(None)

contractFunctionDictionary = {
    "NetworkFeePPMUpdated" : contractNetworkFeePPMUpdated,
    "TradingFeePPMUpdated" : contractTradingFeePPMUpdated,
    "DepositingEnabled" : contractDepositingEnabled,
    "TradingEnabled" : contractTradingEnabled,
    "FundingLimits" : contractFundingLimits,
    "depositTKN" :  contractDepositTkn,
    "WithdrawalInitiated" : contractWithdrawalInitiated,
    "depositBNT" : contractDepositBnt,
    "trade" : contractTrade
}

def securityMonitor(events):
    df = pd.read_csv(events)
    for index in df.index:
        print(index)
        copyRows()
        blockNumber = getContractBlockNumber(df, index)
        newTimestamp(blockNumber)
        txHash = getTxHash(df, index)
        type = df["type"][index]
        function = contractFunctionDictionary[type]
        function(df, index, blockNumber, txHash)

def monitorCharts(monitor):
    monitorTokenDeposits = pd.DataFrame.from_dict(monitor["token deposits"])
    monitorWithdrawalsInitiated = pd.DataFrame.from_dict(monitor["withdrawals initiated"])
    monitorBntDeposits = pd.DataFrame.from_dict(monitor["bnt deposits"])
    monitorTrades = pd.DataFrame.from_dict(monitor["trades"])
    sns.set(rc={
        'axes.facecolor':'black',
        'figure.facecolor':'black',
        'text.color': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white',
        'axes.grid': False,
        'axes.labelcolor': 'white'})
    monitorTokenDeposits.columns
    for monitordict in [monitorTokenDeposits, monitorWithdrawalsInitiated, monitorBntDeposits, monitorTrades]:
        begin = [i for i,c in enumerate(monitordict.keys()) if 'simulated' in c][0]-1
        zippy = list(zip(monitordict.keys()[begin::2],monitordict.keys()[begin+1::2]))
        count = 0
        for i in range(len(zippy)):
            monitordict.loc[:,zippy[i]] = monitordict.loc[:,zippy[i]].astype(float)
            fig = plt.figure()
            fig.set_size_inches(6,6)
            print(zippy[i][0])
            print("Compare max deviation from ethereum vs simulated:")
            print(abs((monitordict.loc[:,zippy[i][1]] - monitordict.loc[:,zippy[i][0]])/monitordict.loc[:,zippy[i][1]]).max())
            sns.lineplot(data = monitordict, x = 'block number', y = (monitordict.loc[:,zippy[i][1]] - monitordict.loc[:,zippy[i][0]])/monitordict.loc[:,zippy[i][1]], color='r')
            plt.show()
            count += 1
    return(None)