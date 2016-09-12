###############################################################################
# Test for the I2C Master HAL
#
###############################################################################
from cocotb.triggers import Timer

from I2CSlaveModelHAL import I2CSlaveModelHAL
from cocotblib.ClockDomain import ClockDomain, RESET_ACTIVE_LEVEL
from spinal.I2CTester.HAL.I2CHAL       import *
from spinal.I2CTester.HAL.I2CMasterHAL import I2CMasterHAL


###############################################################################
# Basic test
@cocotb.test()
def master_hal_basic_tests(dut):

    dut.log.info("Cocotb I2C Master HAL - Basic Test ")

    listOperation = list()
    listOperation.append( [START(), WRITE(-1,0,0,True), ACK(), STOP()]  )    ## Test collision
    listOperation.append( [START(), WRITE(), ACK(), STOP()] )
    listOperation.append( [START(), READ(),  ACK(), STOP()] )
    listOperation.append( [START(), WRITE(), NACK(), WRITE(), NACK(), STOP()] )
    listOperation.append( [START(), READ(),  ACK(),  READ(),  NACK(), STOP()] )
    listOperation.append( [START(), WRITE(), ACK(), START(), READ(),  NACK(), STOP()] )
    listOperation.append( [START(), READ(),  NACK(), START(), WRITE(), NACK(),  STOP()] )

    for operationSeq in listOperation:

        helperMaster = I2CMasterHAL(dut)
        analyser     = I2CHALAnalyser(helperMaster, operationSeq)
        modelSlave   = I2CSlaveModelHAL(helperMaster)

        clockDomain = ClockDomain(dut.clk, 500, dut.resetn, RESET_ACTIVE_LEVEL.LOW)

        cocotb.fork(clockDomain.start())

        # Init IO and wait the end of the reset
        sclClockDivider = 50
        samplingClockDivider = 5
        enCollision = 1
        helperMaster.io.init(sclClockDivider, samplingClockDivider, enCollision)
        yield clockDomain.event_endReset.wait()

        # run
        cocotb.fork(modelSlave.startSlave(operationSeq))
        cocotb.fork(helperMaster.execOperations(operationSeq))
        cocotb.fork(analyser.start())
        yield helperMaster.checkResponse(operationSeq)


        yield Timer(500000)

        # kill all processes
        clockDomain.stop()
        helperMaster.stop()
        modelSlave.stop()
        analyser.stop()

        yield Timer(500000)


    dut.log.info("I2C Master HAL - Basic Test done")

