#include <vector>
#include <iostream>
#include <cassert>

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

    // Assertions to check the input validity
    assert(inputHeight > 0 && inputWidth > 0);
    assert(outputHeight > 0 && outputWidth > 0);
    assert(kernelHeight > 0 && kernelWidth > 0);
    assert(channelsIn > 0 && channelsOut > 0);

    for (int co = 0; co < channelsOut; ++co) {  // over each output channel
        for (int oh = 0; oh < outputHeight; ++oh) {  // over each output height
            for (int ow = 0; ow < outputWidth; ++ow) {  // over each output width
                float acc = 0.0;  // Accumulator for the sum
                for (int ci = 0; ci < channelsIn; ++ci) {  // over each input channel
                    for (int kh = 0; kh < kernelHeight; ++kh) {  // over each kernel height
                        for (int kw = 0; kw < kernelWidth; ++kw) {  // over each kernel width
                            int ih = oh + kh - kernelHeight / 2;  // Input height index with padding handling
                            int iw = ow + kw - kernelWidth / 2;  // Input width index with padding handling
                            if (ih >= 0 && ih < inputHeight && iw >= 0 && iw < inputWidth) {  // Check boundaries
                                int inputIdx = (ci * inputHeight * inputWidth) + (ih * inputWidth) + iw;
                                int weightIdx = ((co * channelsIn + ci) * kernelHeight * kernelWidth) + (kh * kernelWidth) + kw;
                                acc += input[inputIdx] * weights[weightIdx];
                            }
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
}
