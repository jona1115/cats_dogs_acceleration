// Compile using: g++ -shared -o libcustom_conv_delegate.so -fPIC custom_conv.c -I/usr/local/include -L/usr/local/lib -ltensorflowlite_c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tensorflow/lite/c/common.h"

// Example custom convolution implementation
TfLiteStatus CustomConv2D(TfLiteContext* context, TfLiteNode* node) {
    printf("Custom convolution called\n");

    // Get input and output tensors
    const TfLiteTensor* input = &context->tensors[node->inputs->data[0]];
    TfLiteTensor* output = &context->tensors[node->outputs->data[0]];

    // Perform custom convolution (dummy implementation for demonstration)
    memcpy(output->data.raw, input->data.raw, input->bytes);

    return kTfLiteOk;
}

// Delegate data structure
typedef struct {
    TfLiteDelegate base;
    const TfLiteRegistration* original_registration;
} CustomDelegate;

// Delegate node replacement function
TfLiteStatus CustomDelegateReplaceNode(TfLiteContext* context, TfLiteNode* node, TfLiteRegistration* registration, CustomDelegate* custom_delegate) {
    // Save the original registration and replace the invoke function
    custom_delegate->original_registration = registration;
    registration->invoke = CustomConv2D;
    return kTfLiteOk;
}

// Prepare function for the delegate
TfLiteStatus CustomDelegatePrepare(TfLiteContext* context, TfLiteDelegate* delegate) {
    CustomDelegate* custom_delegate = (CustomDelegate*)delegate;
    TfLiteIntArray* execution_plan;
    TF_LITE_ENSURE_STATUS(context->GetExecutionPlan(context, &execution_plan));

    for (int i = 0; i < execution_plan->size; ++i) {
        TfLiteNode* node;
        TfLiteRegistration* registration;
        TF_LITE_ENSURE_STATUS(context->GetNodeAndRegistration(context, execution_plan->data[i], &node, &registration));

        // Check if the node is a convolution operation
        const int kTfLiteBuiltinConv2d = 3;  // Using the numeric value for Conv2D operation
        if (registration->builtin_code == kTfLiteBuiltinConv2d) {
            CustomDelegateReplaceNode(context, node, registration, custom_delegate);
        }
    }
    return kTfLiteOk;
}

// Create a custom delegate that overrides the convolution operator
TfLiteDelegate* CreateCustomConvDelegate() {
    CustomDelegate* custom_delegate = (CustomDelegate*)malloc(sizeof(CustomDelegate));
    if (!custom_delegate) return NULL;

    custom_delegate->base.Prepare = CustomDelegatePrepare;
    custom_delegate->base.flags = kTfLiteDelegateFlagsNone;
    custom_delegate->original_registration = NULL;

    return (TfLiteDelegate*)custom_delegate;
}

// Delegate destroy function (if needed)
void DestroyCustomConvDelegate(TfLiteDelegate* delegate) {
    free(delegate);
}
