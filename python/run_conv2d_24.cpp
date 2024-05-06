/*******************************************************************************************
 *
 * Created by: Jonathan Tan (jona1115@iastate.edu, github.com/jona1115)
 *
 * *****************************************************************************************
 *
 * @file run_conv2d_24.cpp:
 *
 * MODIFICATION HISTORY:
 *
 * Ver   Who       Date	      Changes
 * ----- --------- ---------- ----------------------------------------------
 * 1.00	 Jonathan  5/5/2024
 *
*******************************************************************************************/

// To compile: g++ -fPIC -shared -o lib_run_conv2d_24.so run_conv2d_24.cpp

#include <vector>
#include <iostream>
#include <cassert>

// Convolution operation
// Inputs:
// - input: flat vector representing the input image or feature map
// - weights: flat vector representing the weights of the convolution filter
// - bias: bias term for the convolution filter
// - inputHeight, inputWidth: dimensions of the input image or feature map
// - outputHeight, outputWidth: dimensions of the output feature map
// - kernelHeight, kernelWidth: dimensions of the convolution filter
// - channelsIn: number of input channels
// - channelsOut: number of output channels
// Output:
// - output: flat vector to store the output feature map
extern "C" {
void run_conv2d_24( float* input, int input_size,
                    float* weights, int weights_size,
                    float* bias, int bias_size,
                    int inputHeight, int inputWidth,
                    int outputHeight, int outputWidth,
                    int kernelHeight, int kernelWidth,
                    int channelsIn, int channelsOut,
                    float* output, int output_size
                    ) {


    // std::cout << "inputHeight: " << std::to_string(inputHeight) << "\n";
    // std::cout << "inputWidth: " << std::to_string(inputWidth) << "\n";
    // std::cout << "outputHeight: " << std::to_string(outputHeight) << "\n";
    // std::cout << "outputWidth: " << std::to_string(outputWidth) << "\n";
    // std::cout << "kernelHeight: " << std::to_string(kernelHeight) << "\n";
    // std::cout << "kernelWidth: " << std::to_string(kernelWidth) << "\n";
    // std::cout << "channelsIn: " << std::to_string(channelsIn) << "\n";
    // std::cout << "channelsOut: " << std::to_string(channelsOut) << "\n";

    // std::cout << "Array size (input): " << sizeof(input)/sizeof(float) << "\n";
    // int i = 0;
    // for (i = 0; i < input.size(); ++i) {
    //     std::cout << "input(" << std::to_string(i) << "): " << std::to_string(input[i]) << "\n";
    // }

    // Assertions to check the input validity
    assert(inputHeight > 0 && inputWidth > 0);
    assert(outputHeight > 0 && outputWidth > 0);
    assert(kernelHeight > 0 && kernelWidth > 0);
    assert(channelsIn > 0 && channelsOut > 0);

    for (int co = 0; co < channelsOut; ++co) {  // over each output channel
        // std::cout << "co: " << std::to_string(co) << "\n";
        for (int oh = 0; oh < outputHeight; ++oh) {  // over each output height
            // std::cout << "oh: " << std::to_string(oh) << "\n";
            for (int ow = 0; ow < outputWidth; ++ow) {  // over each output width
                // std::cout << "ow: " << std::to_string(ow) << "\n";
                float acc = 0.0;  // Accumulator for the sum
                for (int ci = 0; ci < channelsIn; ++ci) {  // over each input channel
                    // std::cout << "ci: " << std::to_string(ci) << "\n";
                    for (int kh = 0; kh < kernelHeight; ++kh) {  // over each kernel height
                        // std::cout << "kh: " << std::to_string(kh) << "\n";
                        for (int kw = 0; kw < kernelWidth; ++kw) {  // over each kernel width
                            // std::cout << "kw: " << std::to_string(kw) << "\n";
                        
                            int ih = oh + kh;  // Input height index
                            // std::cout << "after int ih = oh + kh;\n";
                            int iw = ow + kw;  // Input width index
                            // std::cout << "after int iw = ow + kw;\n";
                            // Calculate the index for the input and weight
                            int inputIdx = (ci * inputHeight * inputWidth) + (ih * inputWidth) + iw;
                            // std::cout << "inputIdx: " << std::to_string(inputIdx) << "\n";
                            int weightIdx = ((co * channelsIn + ci) * kernelHeight * kernelWidth) + (kh * kernelWidth) + kw;
                            // std::cout << "weightIdx: " << std::to_string(weightIdx) << "\n";
                            acc += input[inputIdx] * weights[weightIdx];
                            // std::cout << "after acc += input[inputIdx\n";
                        }
                    }
                }
                acc += bias[co];  // Add the bias term
                int outputIdx = (co * outputHeight * outputWidth) + (oh * outputWidth) + ow;
                output[outputIdx] = acc;
            }
        }
    }
}
} // Close of extern "C"