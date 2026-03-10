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
    on_start.value_list = ["Time;Value"]

    return result

def on_trigger(input):
    result = StreamManipulator.OutputData()
    data = on_init.stream.read_data()

    if len(data) > 1 and len(data[0]) > 0:
        wavelengths = data[0]
        times = data[1]
        input.OutputStreams[0].Samples.append(DataStreamInstrument.BasicSample(wavelengths[-1] *1e9, times[-1]))
        data_string = f"{wavelengths[-1] *1e9};{times[-1]}"
        on_start.value_list.append(data_string)

    if len(data[0]) > 1:
        result.LastConsumedSampleIDsPerInputStream.append(data[0].ConsumeAll())
        result.LastConsumedSampleIDsPerInputStream.append(data[1].ConsumeAll())

    return result


def on_finished(input):
    result = StreamManipulator.OutputData()

    filename = f"{input.SaveFilename}_wavelength.csv"
    try:
        with open(filename, "w") as file:
            file.write("\n".join(on_start.value_list))
        print(f"{filename} saved successfully.")
    except Exception as e:
        print(f"Error during saving data: {e}")

    if hasattr(on_init, 'value_list'):
        del on_start.value_list

    return result

def on_exit():
    on_init.stream.stop_stream()
    on_init.connection.close()