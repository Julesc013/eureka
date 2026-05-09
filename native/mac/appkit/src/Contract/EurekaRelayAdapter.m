#import "EurekaRelayAdapter.h"

@implementation EurekaRelayAdapter

+ (BOOL)textLooksReadOnly:(NSString *)text
{
    if (text == nil) {
        return NO;
    }
    if ([text rangeOfString:@"localhost_readonly"].location != NSNotFound) {
        return YES;
    }
    return [text rangeOfString:@"read_only"].location != NSNotFound;
}

+ (NSString *)fixtureSummary
{
    return @"Relay: localhost/read-only fixture status display only.";
}

@end
