import datetime
import rpyc

def on_init(input):
    host = '141.20.45.252'
    port = '12345'
    module_name = 'wavemeter_cwave'

    protocol_config = {
        'allow_all_attrs': True,
        'allow_setattr': True,
        'allow_delattr': True,
        'allow_pickle': True,
        'sync_request_timeout': 3600
    }

    on_init.connection = rpyc.connect(host=host, port=port, config=protocol_config)
    on_init.stream = on_init.connection.root.get_module_instance(module_name)

    on_init.value_unit = on_init.stream.constraints.channel_units
    on_init.stream.start_stream()

def on_start(input):
    result = StreamManipulator.OutputData()
    input.OutputStreams[0].Clear()
    input.OutputStreams[1].Clear()
    on_start.value_list = ["Time;Wavelength;APD"]

    return result

def on_trigger(input):
    result = StreamManipulator.OutputData()
    WLM_data = on_init.stream.read_data()

    if len(WLM_data) > 1 and len(WLM_data[0]) > 0 and len(input.InputStreams[0].Samples) > 0:
        WLM_value = WLM_data[0]
        WLM_time = WLM_data[1]
        APD_value = input.InputStreams[0].Samples[-1].Value
        APD_time = input.InputStreams[0].Samples[-1].Time
        input.OutputStreams[0].Samples.append(DataStreamInstrument.BasicSample(WLM_value[-1] *1e9, WLM_time[-1]))
        input.OutputStreams[1].Samples.append(DataStreamInstrument.BasicSample(APD_value, APD_time))
        data_string = f"{WLM_time[-1]};{APD_time};{WLM_value[-1] *1e9};{APD_value}"
        on_start.value_list.append(data_string)

    if len(input.InputStreams) > 1:
        result.LastConsumedSampleIDsPerInputStream.append(input.InputStreams[0].ConsumeAll())
        result.LastConsumedSampleIDsPerInputStream.append(input.InputStreams[1].ConsumeAll())

    #if len(WLM_data[0]) > 1:
    #    result.LastConsumedSampleIDsPerInputStream.append(WLM_data[0].ConsumeAll())
    #    result.LastConsumedSampleIDsPerInputStream.append(WLM_data[1].ConsumeAll())

    return result


def on_finished(input):
    result = StreamManipulator.OutputData()
    filename = f"WL_and_APD_data_2.csv"
    #filename = f"{input.SaveFilename}_WL_and_APD.csv"
    try:
        with open(filename, "w") as file:
            file.write("\n".join(on_start.value_list))
        print(f"{filename} saved successfully.")
    except Exception as e:
        print(f"Error during saving data: {e}")

    if hasattr(on_init, 'value_list'):
        del on_start.value_list

    return result

def on_exit(input):
    on_init.stream.stop_stream()
    on_init.connection.close()