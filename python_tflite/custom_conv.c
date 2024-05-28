// custom_conv.c
#include "tensorflow/lite/c/common.h"
// #include "/home/petalinux/tensorflow/tensorflow/lite/c/common.h"
// #include "/home/petalinux/tensorflow/tensorflow/lite/c/c_api_internal.h"

#include <cstring>
#include <cstdlib>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Example custom convolution implementation
TfLiteStatus CustomConv2D(TfLiteContext* context, TfLiteNode* node) {
    printf("Custom convolution called\n");

    // Get input and output tensors
    TfLiteTensor* input = &context->tensors[node->inputs->data[0]];
    TfLiteTensor* output = &context->tensors[node->outputs->data[0]];

    // Perform custom convolution (dummy implementation for demonstration)
    memcpy(output->data.raw, input->data.raw, input->bytes);

    return kTfLiteOk;
}

// Replace the convolution operator with custom implementation
TfLiteStatus ReplaceConvolutionOperator(TfLiteContext* context) {
    for (int i = 0; i < context->tensors_size; ++i) {
        const TfLiteRegistration* registration = context->GetNodeAndRegistration(context, i, NULL);
        if (registration != NULL && registration->builtin_code == kTfLiteBuiltinConv2d) {
            // Get node and modify the invoke function
            TfLiteNode* node;
            context->GetNodeAndRegistration(context, i, &node);
            node->builtin_code = registration->builtin_code;
            node->user_data = registration->user_data;
            node->delegate = registration->delegate;
            ((TfLiteRegistration*)registration)->invoke = CustomConv2D;
        }
    }
    return kTfLiteOk;
}

// Create a custom delegate that overrides the convolution operator
TfLiteDelegate* CreateCustomConvDelegate() {
    TfLiteDelegate* delegate = (TfLiteDelegate*)malloc(sizeof(TfLiteDelegate));
    if (!delegate) return NULL;

    delegate->Prepare = [](TfLiteContext* context, TfLiteDelegate* delegate) -> TfLiteStatus {
        return ReplaceConvolutionOperator(context);
    };

    delegate->CopyFromBufferHandle = NULL;
    delegate->CopyToBufferHandle = NULL;
    delegate->FreeBufferHandle = NULL;

    return delegate;
}
