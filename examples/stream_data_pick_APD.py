def on_start(input):    
    result = StreamManipulator.OutputData() 
    input.OutputStreams[0].Clear() 

    on_start.value_list = ["Time;Value"]
    
    return result 

def on_trigger(input): 
    result = StreamManipulator.OutputData() 

    if len(input.InputStreams[0].Samples) > 0:
        latest_sample = input.InputStreams[0].Samples[-1]
        input.OutputStreams[0].Samples.append(DataStreamInstrument.BasicSample(
            latest_sample.Value, latest_sample.Time))
        data_string = f"{latest_sample.Time};{latest_sample.Value}"
        on_start.value_list.append(data_string) 

    if len(input.InputStreams) > 1: 
        result.LastConsumedSampleIDsPerInputStream.append(input.InputStreams[0].ConsumeAll()) 
        result.LastConsumedSampleIDsPerInputStream.append(input.InputStreams[1].ConsumeAll()) 
     
    return result 

def on_finished(input): 
    result = StreamManipulator.OutputData() 

    filename = "dataAPD.csv"
    #filename = f"{input.SaveFilename}_APD.csv"
    try:
        with open(filename, "w") as file:
            file.write("\n".join(on_start.value_list))
        print(f"{filename} saved successfully.")
    except Exception as e:
        print(f"Error during saving data: {e}")

    if hasattr(on_start, 'value_list'):
        del on_start.value_list

    return result