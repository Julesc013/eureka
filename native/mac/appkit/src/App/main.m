#import <Cocoa/Cocoa.h>
#import "EurekaAppDelegate.h"

int main(int argc, const char *argv[])
{
    @autoreleasepool {
        NSApplication *application;
        EurekaAppDelegate *delegate;

        (void)argc;
        (void)argv;
        application = [NSApplication sharedApplication];
        delegate = [[EurekaAppDelegate alloc] init];
        [application setDelegate:delegate];
        [application run];
    }
    return 0;
}
