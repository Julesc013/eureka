#import <Foundation/Foundation.h>

@interface EurekaSnapshotAdapter : NSObject
+ (BOOL)textLooksLikeSnapshot:(NSString *)text;
+ (NSString *)fixtureSummary;
@end
